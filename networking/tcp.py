import socket
import queue
import threading
import logging

logger = logging.getLogger(__name__) #Get logger from main 


class TcpServer(threading.Thread):

    BUFFER_SIZE = 1024

    def __init__(self, ip, port):
        super().__init__()
        self.mainqueuerecv = queue.Queue() #set up the main queue that will send the received data to process it
        self.mainqueuesend = queue.Queue() #set up main queue that will send the data to the node 
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # use tcp
        self.s.bind((ip, port)) #bind the ip and the port 
        self.s.listen(10) # Start to listen with a max of 10 incoming connections
        self.connlist = {}
        threading.Thread(target=self.SendToAddr).start()
        self.start()
    
    def run(self):
        while True:
            conn, addr = self.s.accept() #accept incoming connection
            logger.debug("{} connected to server.".format(addr))
            t = threading.Thread(target=self.ConnToNodeThread, args=(conn, addr,)) #Create a new thread
            self.connlist[len(self.connlist)] = {'obj': conn, 'addr': addr, 'thread':t, 'conninit':False} #add connection to list for future use
            t.start() #Start the thread that will receive the data

    def RemoveNodeFromList(self, addr):
        connid = None 
        for i in self.connlist: #Loop through connected node list and tries to find the connected node 
            if self.connlist[i]['addr'] == addr:
                connid = i
                break
            else:
                logger.warning("{} wasn't in node connection list".format(addr))
                return
            del self.connlist[connid] #delete connected node from the list

    def ConnToNodeThread(self, conn, addr): #Function that manages one connection
        while True:
            try:
                packet = conn.recv(self.BUFFER_SIZE).split(b'\x00\x00\x00\x00\x00\x00') #Get data from the node
                data = b''
                msg_len = int(packet[0].decode("utf-8"))
                data += packet[1]
                while len(data) <  msg_len:
                    packett = conn.recv(self.BUFFER_SIZE)
                    data += packett
            except ConnectionResetError:
                self.RemoveNodeFromList(addr)
                logger.debug("{} disconnected from the server".format(addr))
                break #Exit the thread if node disconnects from the server
            if not data:
                self.RemoveNodeFromList(addr)
                logger.debug("{} disconnected from the server".format(addr))
                break #Exit the thread if node disconnects from the server
            if data == b'conninit':
                for i in self.connlist:
                    if addr == self.connlist[i]['addr']:
                        self.connlist[i]['conninit'] = True
                        break
                else:
                    logger.warning("Can't find {} in connection list".format(addr))
            self.mainqueuerecv.put((addr, data)) #Put the data and the address on the queue to process it 
    
    def SendToAddr(self):
        while True:
            queuedata = self.mainqueuesend.get() #Get Parser message to send to addr
            addr = queuedata[0]
            message = queuedata[1]
            conn = None
            for i in self.connlist: #Get conn from node connected list
                if self.connlist[i]['addr'] == addr:
                    conn = self.connlist[i]['obj']
                    break
            else:
                logger.warning("{} wasn't in node connection list. Aborting...".format(addr))
                continue
            conn.send(str(len(message)).encode("utf-8") + b'\x00\x00\x00\x00\x00\x00' + message) #Finally send the message to the node

class TcpClient(threading.Thread):

    BUFFER_SIZE = 1024

    def __init__(self, ip, port): 
        super().__init__()
        self.ip = ip
        self.port = port
        self.mainqueuerecv = queue.Queue()
        self.mainqueuesend = queue.Queue()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # use tcp
        self.s.connect((self.ip, self.port))
        self.s.send(str(len(b"conninit")).encode("utf-8") + b'\x00\x00\x00\x00\x00\x00' + b"conninit") #send init packet to make sure that is the server
        threading.Thread(target=self.SendToServer).start() #thread to send
        self.start()

    def run(self):
        while True:
            try:
                packet = self.s.recv(self.BUFFER_SIZE).split(b'\x00\x00\x00\x00\x00\x00') #Get data from the node
                data = b''
                msg_len = int(packet[0].decode("utf-8"))
                data += packet[1]
                while len(data) <  msg_len:
                    packett = self.s.recv(self.BUFFER_SIZE)
                    data += packett
            except ConnectionResetError: # detect if the connection has been reset
                logger.fatal("Connection lost from the server on {}.".format(self.ip))
                break
            self.mainqueuerecv.put(data)

    def SendToServer(self):
        while True:
            data = self.mainqueuesend.get() #get data from the parser
            self.s.send(str(len(data)).encode("utf-8") + b'\x00\x00\x00\x00\x00\x00' + data)