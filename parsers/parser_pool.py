import threading
import logging
import inspect #Using inpect to get the required args for each parser
import sys
sys.path.append('../')
import variables
import system
import networking

logger = logging.getLogger(__name__)

class ParserPool(threading.Thread):
    """
        This Class will manage all parsers used in Carnotaurs for 
        easy managing of threads and also create new threads
        if old ones crash.
    """

    #This is a list of all parsers, they can be added while running for a future plugin support
    #Every parser must have it's own type CLIENT or SERVER and it's args in order 
    parser_list = {
        'networking_client' : {'type': "CLIENT", 'obj':networking.TcpClientParser, 'args': list(inspect.getargspec(networking.TcpClientParser)[0]), 'active': False},
        'networking_server' : {'type': "SERVER", 'obj':networking.TcpParser, 'args': list(inspect.getargspec(networking.TcpParser)[0]), 'active': False}
    }

    def __init__(self, **kwargs): 
        super().__init__()
        self._kwargs = kwargs #Kwargs is needed because it's needed a infinite number of args for n parsers, each parser has it's own requirements like the ip address.
        self.InitializeAllParsers()

    def InitializeAllParsers(self):
        for e in self.parser_list:
            if variables.typee == self.parser_list[e]["type"]: #Check if parser matches the current type
                needed_args = [] 
                for i in self._kwargs: #Get all arguments needed for initializing the parser
                    if i in self.parser_list[e]['args']:
                        needed_args.append(self._kwargs[i])
                logging.info("Trying to initialize {} parser".format(e))
                self.parser_list[e]['initobj'] = self.parser_list[e]['obj'](*needed_args) #Try to initialize the parser
                logging.info("Initialized sucessfully {} parser".format(e))
                self.parser_list[e]['active'] = True
