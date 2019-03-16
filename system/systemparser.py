import logging
import queue
import threading

logger = logging.getLogger(__name__)

class SystemParser(threading.Thread):
    """
        A sub-parser to process system related functions, usually from the server.
    """

    def __init__(self, interparserqueue):
        self.queuerecv = interparserqueue
        self.start()

    def run(self):
        while True:
            data = self.queuerecv.get() #On a sub-parser the data must be decrypted and in a dictionary to easier use
            