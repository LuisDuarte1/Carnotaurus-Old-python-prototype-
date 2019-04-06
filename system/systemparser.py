import logging
import queue
import threading
import sys
from system import GetCpuUsage, GetFreeRam, GetProcessList, GetSpecs
import time
sys.path.append('../')
import json
import variables

logger = logging.getLogger(__name__)

class SystemParser(threading.Thread):
    """
        A sub-parser to process system related functions, usually from the server.
    """

    deltatime_stats = 10

    def __init__(self, interparserqueue):
        super().__init__()
        self.queuerecv = interparserqueue
        self.parser_comms = None
        threading.Thread(target=self.GetInterParserQueue).start()
        if variables.typee == 'SERVER':
            threading.Timer(self.deltatime_stats ,self.GetStatsFromAllClients).start()
        self.start()

    def GetInterParserQueue(self):
        while variables.parser_poolobj == None: #Check if parser_pool obj is initialized
            continue
        self.parser_comms = variables.parser_poolobj.InterParserQueue
        logger.debug("Got the interparser queue...")

    def GetStatsFromAllClients(self):
        self.parser_comms.put({'to': 'networking_server', 'action':'sendall', 'to_send':'{"type":"system", "action":"get_all_stats"}'})
        threading.Timer(self.deltatime_stats ,self.GetStatsFromAllClients).start()


    def run(self):
        while True:
            data = self.queuerecv.get() #On a sub-parser the data must be decrypted and in a dictionary to easier use
            if variables.typee == 'SERVER': #Process exclusive data from the clients
                pass
            elif variables.typee == 'CLIENT': #Process exclusive data from the server
                if data['action'] == 'get_all_stats':
                    stats = {
                        'cpu_usage': GetCpuUsage(2),
                        'free_ram': GetFreeRam(),
                        'process_list': GetProcessList()
                    }
                    self.parser_comms.put({
                        'to': 'networking_client',
                        'action': 'sendserver',
                        'to_send': json.dumps({'type':"system", 'action':'process_stat_data', 'data':stats})
                        })