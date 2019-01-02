import threading
import logging

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
            self.mainqueuesend.put((addr, data))