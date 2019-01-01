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
        self.mainqueuesend = queue.Queue() #set um main queue that will send the data to the node 
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # use tcp
        self.s.bind((ip, port)) #bind the ip and the port 
        self.s.listen(10) # Start to listen with a max of 10 incoming connections
        self.connlist = {}
        self.start()
    
    def run(self):
        while True:
            conn, addr = self.s.accept() #accept incoming connection
            logger.debug("{} connected to server.".format(addr))
            t = threading.Thread(target=self.ConnToNodeThread, args=(conn, addr,)) #Create a new thread
            self.connlist[len(self.connlist)] = {'obj': conn, 'addr': addr, 'thread':t} #add connection to list for future use
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
                data = conn.recv(self.BUFFER_SIZE) #Get data from the node
            except ConnectionResetError:
                self.RemoveNodeFromList(addr)
                logger.debug("{} disconnected from the server".format(addr))
                break #Exit the thread if node disconnects from the server
            if not data:
                self.RemoveNodeFromList(addr)
                logger.debug("{} disconnected from the server".format(addr))
                break #Exit the thread if node disconnects from the server
            self.mainqueuerecv.put((addr, data)) #Put the data and the address on the queue to process it 