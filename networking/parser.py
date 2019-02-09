import threading
import logging
import datetime
from time import sleep
import crypto

logger = logging.getLogger(__name__)

class TcpParser(threading.Thread):

    def __init__(self, mainqueuerecv, mainqueuesend):
        super().__init__()
        self.mainqueuerecv = mainqueuerecv #Declare queue from tcp server
        self.mainqueuesend = mainqueuesend #Declare queue from tcp server
        self.server_rsa = crypto.RSA(True) #Initialize RSA creating a private key
        self.client_rsa = {}
        self.start() #Start the main parser thread
    
    def SendDataToClient(self, addr, message):
        if type(message) != bytes:
            raise TypeError("Message must be in bytes instead of {}".format(type(message)))
        encrypted_comms_client = False
        rsaobj = None
        for i in self.client_rsa:
            if self.client_rsa[i]['addr'] == addr:
                encrypted_comms_client = self.client_rsa[i]['cryptocomms']
                rsaobj = self.client_rsa[i]['rsaobj']
                break
        if encrypted_comms_client == False:
            self.mainqueuesend.put((addr, message))
        else:
            if rsaobj != None:
                self.mainqueuesend.put((addr,rsaobj.Encrypt(message)))
            else:
                self.mainqueuesend.put((addr, message))


    def run(self):
        while True:
            datafromtcpserver = self.mainqueuerecv.get() #Get the data from the queue
            data = datafromtcpserver[1]
            addr = datafromtcpserver[0]
            if data == b'conninit':
                self.mainqueuesend.put((addr, b'connrecv'))
                continue
            if data == b'hr':
                self.mainqueuesend.put((addr, b'hrok'))
                continue
            if b'-----BEGIN PUBLIC KEY-----' in data:
                rsa = crypto.RSA(False)
                rsa.LoadPublicKey(data)
                self.client_rsa[str(len(self.client_rsa))] = {'addr': addr, 'rsaobj':rsa, 'cryptocomms': False}
                self.mainqueuesend.put((addr, rsa.Encrypt(self.server_rsa.GetPublicKey())))
                continue
            if b'crypto_ok' in data: #Start using encrypted comms instead of non-encrypted comms
                for i in self.client_rsa:
                    if self.client_rsa[i]['addr'] == addr:
                        logger.debug("{} is now using encrypted communication".format(addr))
                        self.client_rsa[i]['cryptocomms'] = True
                        break
            logger.debug(data)
            self.mainqueuesend.put((addr, data))


class TcpClientParser(threading.Thread):

    HEARTBEAT_TIME = 1800 #Every 30 minutes send a heartbeat to make sure that the connection is alive
    NOHEARTBEAT_TIMEOUT = HEARTBEAT_TIME * 2

    def __init__(self, mainqueuerecv, mainqueuesend):
        super().__init__()
        self.mainqueuerecv = mainqueuerecv #Declare queue from tcp server to get the data
        self.mainqueuesend = mainqueuesend #Declare queue from tcp server to send data
        self.client_rsa = crypto.RSA(True) #Initialize RSA creating a private key
        self.server_rsa = crypto.RSA(False) #Initialize RSA without create a key for future encryption to the server
        self.connection_encrypted = False
        self.lastheartbeat = datetime.datetime.now()
        threading.Thread(target=self.Heartbeat).start() #Start Heartbeat thread
        threading.Thread(target=self.HeartbeatTimeout).start() #Start another heartbeat thread if the server dosent respond to exit Carnotaurus 
        self.start() #Start the main parser thread
    
    def HeartbeatTimeout(self):
        while True:
            sleep(self.HEARTBEAT_TIME * 1.25)
            timesincehr = datetime.datetime.now() - self.lastheartbeat
            if timesincehr.total_seconds() >= self.NOHEARTBEAT_TIMEOUT:
                logging.fatal("Server didint respond to heartbeat for {} seconds".format(timesincehr.total_seconds()))

    def SendToServer(self, message):
        if type(message) == bytes:
            if self.connection_encrypted == True:
                self.mainqueuesend.put(self.server_rsa.Encrypt(message))
            else:
                self.mainqueuesend.put(message)
        else:
            raise TypeError("Message was in {} instead of bytes".format(type(message)))


    def Heartbeat(self):
        while True:
            self.SendToServer(b'hr')
            sleep(self.HEARTBEAT_TIME)


    def run(self):
        while True:
            datasv = self.mainqueuerecv.get()
            try:
                datasv.decode("utf-8")
            except UnicodeDecodeError: #When the data isn't plaintext, try to decrypt it
                datasv = self.client_rsa.Decrypt(datasv)
            if datasv == b'hrok':
                self.lastheartbeat = datetime.datetime.now()
                continue
            if datasv == b'connrecv': #When the connection is succesful, start the key-exchange process
                self.SendToServer(self.client_rsa.GetPublicKey()) 
            if b'-----BEGIN PUBLIC KEY-----' in datasv: #Load server public key to encrypt the data 
                self.server_rsa.LoadPublicKey(datasv)
                self.connection_encrypted = True
                self.SendToServer(b'crypto_ok')
