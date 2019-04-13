import threading
from clients import ClientDatabase
import variables
import logging

logger = logging.getLogger(__name__)

class ClientParser(threading.Thread):

    """
    Parser to store all related client information
    """
    def __init__(self, interparserqueue):
        super().__init__()
        self.interparserqueue = interparserqueue
        self.parser_comms = None
        self.uuid_ip = {}
        threading.Thread(target=self.GetInterParserQueue).start()
        self.start()
    
    def GetInterParserQueue(self):
        while variables.parser_poolobj == None: #Check if parser_pool obj is initialized
            continue
        self.parser_comms = variables.parser_poolobj.InterParserQueue
        logger.debug("Got the interparser queue...")

    def run(self):
        self.db = ClientDatabase("clients.db")
        while True:
            data = self.interparserqueue.get()
            if data['action'] == 'process_uuid':
                if self.db.CheckIfUUIDExists(data['uuid']) == False:
                    logger.debug("Looks like that this client dosen't yet exist.. Adding it to the data base")
                    self.db.AddClient(data['uuid'])
                    self.db.AddIpToUUID(data['uuid'], data['addr'])
                else:
                    self.db.AddIpToUUID(data['uuid'], data['addr']) #Update existing IP
