import threading
import logging
import datetime
from time import sleep
import crypto
import variables

logger = logging.getLogger(__name__)

class TcpParser(threading.Thread):

    def __init__(self, mainqueuerecv, mainqueuesend, interparserqueue):
        super().__init__()
        self.mainqueuerecv = mainqueuerecv #Declare queue from tcp server
        self.mainqueuesend = mainqueuesend #Declare queue from tcp server
        self.server_rsa = crypto.RSA(True) #Initialize RSA creating a private key
        self.interparserqueue = interparserqueue #Declare queue to get the data from the other parsers
        self.parser_comms = None
        threading.Thread(target=self.GetInterParserQueue).start() #Get interparser queue to send data to other parsers
        self.client_rsa = {}
        self.start() #Start the main parser thread
    
    def GetInterParserQueue(self):
        while variables.parser_poolobj == None: #Check if parser_pool obj is initialized
            continue
        self.parser_comms = variables.parser_poolobj.InterParserQueue
        logger.debug("Got the interparser queue...")

    def InterParser(self):
        while True:
            data = self.interparserqueue.get()

    def SendDataToClient(self, addr, message):
        if type(message) != bytes:
            raise TypeError("Message must be in bytes instead of {}".format(type(message)))
        encrypted_comms_client = False
        rsaobj = None
        use_rsa = None
        aesobj = None
        for i in self.client_rsa:
            if self.client_rsa[i]['addr'] == addr: #Get All Attributes needed to send data from the dictionary
                encrypted_comms_client = self.client_rsa[i]['cryptocomms']
                rsaobj = self.client_rsa[i]['rsaobj']
                use_rsa = self.client_rsa[i]['use_rsa']
                aesobj = self.client_rsa[i]['aesobj']
                break
        if encrypted_comms_client == False:
            self.mainqueuesend.put((addr, message))
        else:
            if rsaobj != None and use_rsa == True:
                self.mainqueuesend.put((addr, rsaobj.Encrypt(message))) #Encrypt using the client RSA key
            else:
                if aesobj != None and use_rsa == False:
                    self.mainqueuesend.put((addr, aesobj.Encrypt(message))) #Encrypt using the shares AES key
                else:
                    self.mainqueuesend.put((addr, message))

    def DecryptData(self, addr, data):
        for i in self.client_rsa:
            if self.client_rsa[i]['addr'] == addr: #Search for Node Keys
                if self.client_rsa[i]['use_rsa'] == True: #Check if it's to use RSA (RSA is only used for key exchange) or AES
                    return self.server_rsa.Decrypt(data) #If it's rsa, decrypt the data
                else:
                    if self.client_rsa[i]['aesobj'] != None: #Check if the aesobj is initialized 
                        return self.client_rsa[i]['aesobj'].Decrypt(data)
        else:
            logger.fatal("{} wasn't in the encrypted connection list".format(addr))

    def run(self):
        while True:
            datafromtcpserver = self.mainqueuerecv.get() #Get the data from the queue
            data = datafromtcpserver[1]
            addr = datafromtcpserver[0]
            try:
                data.decode("utf-8")
            except UnicodeDecodeError:
                data = self.DecryptData(addr, data)
            logger.debug(data)
            if data == b'conninit':
                self.mainqueuesend.put((addr, b'connrecv'))
                continue
            if data == b'hr':
                self.mainqueuesend.put((addr, b'hrok'))
                continue
            if b'-----BEGIN PUBLIC KEY-----' in data:
                rsa = crypto.RSA(False)
                rsa.LoadPublicKey(data)
                self.client_rsa[str(len(self.client_rsa))] = {'addr': addr, 'rsaobj':rsa, 'cryptocomms': False, 'use_rsa':True, 'aesobj':None}
                self.SendDataToClient(addr, self.server_rsa.GetPublicKey())
                for i in self.client_rsa:
                    if self.client_rsa[i]['addr'] == addr:
                        self.client_rsa[i]['cryptocomms'] = True
                continue
            if b'key' in data and b'iv' in data:
                for i in self.client_rsa:
                    if self.client_rsa[i]['addr'] == addr:
                        aes = crypto.AES(False) 
                        aes.LoadKey(data) #Try to load the AES key
                        self.client_rsa[i]['aesobj'] = aes 
                        self.client_rsa[i]['use_rsa'] = False #Stop using RSA for encryption and start using AES
                        self.client_rsa[i]['rsaobj'] = None #Delete the RSA key to free up some memory
                        self.SendDataToClient(addr, b'aes_ok') #Send to client that the server accepted the aes key
                        logger.debug("{} is now using encrypted communication".format(addr))
                        break
                continue
class TcpClientParser(threading.Thread):

    HEARTBEAT_TIME = 1800 #Every 30 minutes send a heartbeat to make sure that the connection is alive
    NOHEARTBEAT_TIMEOUT = HEARTBEAT_TIME * 2

    def __init__(self, mainqueuerecv, mainqueuesend, interparserqueue):
        super().__init__()
        self.mainqueuerecv = mainqueuerecv #Declare queue from tcp server to get the data
        self.mainqueuesend = mainqueuesend #Declare queue from tcp server to send data
        self.interparserqueue = interparserqueue #Declare queue to get the data from the other parsers
        self.parser_comms = None
        threading.Thread(target=self.GetInterParserQueue).start() #Get interparser queue to send data to other parsers
        self.client_rsa = crypto.RSA(True) #Initialize RSA creating a private key
        self.server_rsa = crypto.RSA(False) #Initialize RSA without create a key for future encryption to the server´
        self.aes = crypto.AES(True) #Initialize AES for using after the key exchange
        self.use_rsa = True #Only use RSA on the key exchange
        self.connection_encrypted = False
        self.lastheartbeat = datetime.datetime.now()
        threading.Thread(target=self.Heartbeat).start() #Start Heartbeat thread
        threading.Thread(target=self.HeartbeatTimeout).start() #Start another heartbeat thread if the server dosent respond to exit Carnotaurus 
        self.start() #Start the main parser thread
    

    def GetInterParserQueue(self):
        while variables.parser_poolobj == None: #Check if parser_pool obj is initialized
            continue
        self.parser_comms = variables.parser_poolobj.InterParserQueue
        logger.debug("Got the interparser queue...")

    def InterParser(self):
        while True:
            data = self.interparserqueue.get()

    def HeartbeatTimeout(self):
        while True:
            sleep(self.HEARTBEAT_TIME * 1.25)
            timesincehr = datetime.datetime.now() - self.lastheartbeat
            if timesincehr.total_seconds() >= self.NOHEARTBEAT_TIMEOUT:
                logging.fatal("Server didint respond to heartbeat for {} seconds".format(timesincehr.total_seconds()))

    def SendToServer(self, message):
        if type(message) == bytes:
            if self.connection_encrypted == True:
                if self.use_rsa == True:
                    self.mainqueuesend.put(self.server_rsa.Encrypt(message))
                else:
                    self.mainqueuesend.put(self.aes.Encrypt(message))
            else:
                self.mainqueuesend.put(message)
        else:
            raise TypeError("Message was in {} instead of bytes".format(type(message)))


    def Heartbeat(self):
        while True:
            self.SendToServer(b'hr')
            sleep(self.HEARTBEAT_TIME)

    def DecryptServerData(self, data):
        if self.use_rsa == True:
            return self.client_rsa.Decrypt(data)
        else:
            return self.aes.Decrypt(data)

    def run(self):
        while True:
            datasv = self.mainqueuerecv.get()
            try:
                datasv.decode("utf-8")
            except UnicodeDecodeError: #When the data isn't plaintext, try to decrypt it
                datasv = self.DecryptServerData(datasv)
            logger.debug(datasv)
            if datasv == b'hrok':
                self.lastheartbeat = datetime.datetime.now()
                continue
            if datasv == b'connrecv': #When the connection is succesful, start the key-exchange process
                self.SendToServer(self.client_rsa.GetPublicKey())
                continue 
            if b'-----BEGIN PUBLIC KEY-----' in datasv: #Load server public key to encrypt the data 
                logging.debug("Recived the server public key")
                self.server_rsa.LoadPublicKey(datasv)
                self.connection_encrypted = True
                self.SendToServer(self.aes.GetKey())
                self.use_rsa = False
                continue
            if datasv == b'aes_ok':
                continue