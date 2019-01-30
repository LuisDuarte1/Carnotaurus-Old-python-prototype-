import threading
import logging
import datetime
from time import sleep

logger = logging.getLogger(__name__)

class TcpParser(threading.Thread):

    def __init__(self, mainqueuerecv, mainqueuesend):
        super().__init__()
        self.mainqueuerecv = mainqueuerecv #Declare queue from tcp server
        self.mainqueuesend = mainqueuesend #Declare queue from tcp server
        self.start() #Start the main parser thread
    
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
            logger.debug(data)
            self.mainqueuesend.put((addr, data))


class TcpClientParser(threading.Thread):

    HEARTBEAT_TIME = 1800 #Every 30 minutes send a heartbeat to make sure that the connection is alive
    NOHEARTBEAT_TIMEOUT = HEARTBEAT_TIME * 2

    def __init__(self, mainqueuerecv, mainqueuesend):
        super().__init__()
        self.mainqueuerecv = mainqueuerecv #Declare queue from tcp server
        self.mainqueuesend = mainqueuesend #Declare queue from tcp server
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


    def Heartbeat(self):
        while True:
            self.mainqueuesend.put(b'hr')
            sleep(self.HEARTBEAT_TIME)


    def run(self):
        while True:
            datasv = self.mainqueuerecv.get()
            if datasv == b'hrok':
                self.lastheartbeat = datetime.datetime.now()
                continue