import logging
import queue
import threading
import variables

logger = logging.getLogger(__name__)

class SystemParser(threading.Thread):
    """
        A sub-parser to process system related functions, usually from the server.
    """

    def __init__(self, interparserqueue):
        super().__init__()
        self.queuerecv = interparserqueue
        threading.Thread(target=self.GetInterParserQueue).start()
        self.start()

    def GetInterParserQueue(self):
        while variables.parser_poolobj == None: #Check if parser_pool obj is initialized
            continue
        self.parser_comms = variables.parser_poolobj.InterParserQueue
        logger.debug("Got the interparser queue...")

    def run(self):
        while True:
            data = self.queuerecv.get() #On a sub-parser the data must be decrypted and in a dictionary to easier use
            