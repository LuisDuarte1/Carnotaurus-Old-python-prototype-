import threading
import logging
import inspect #Using inpect to get the required args for each parser
import sys
import queue
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
    #The must important parsers must be ordered from most important to least important
    #Empty types e.g.: "" means that the parser should run on both client and server 
    parser_list = {
        'networking_client' : {'type': "CLIENT", 'obj':networking.TcpClientParser, 'args': list(inspect.getargspec(networking.TcpClientParser)[0]), 'active': False},
        'networking_server' : {'type': "SERVER", 'obj':networking.TcpParser, 'args': list(inspect.getargspec(networking.TcpParser)[0]), 'active': False},
        'system': {'type': "", 'obj':system.SystemParser, 'args':list(inspect.getargspec(system.SystemParser)[0]), 'active':False}
    }

    def __init__(self, **kwargs): 
        super().__init__()
        self.InterParserQueue = queue.Queue()
        variables.parser_poolobj = self
        logger.info("Initializing Inter parser communication...")
        threading.Thread(target=self.InterParserCommunication).start() #Start a thread for InterParserCommunication
        logger.info("Done initializing Inter parser communication...")
        self._kwargs = kwargs #Kwargs is needed because it's needed a infinite number of args for n parsers, each parser has it's own requirements like the ip address.
        self.InitializeAllParsers()

    def InterParserCommunication(self):
        while True:
            data = self.InterParserQueue.get() #Get data from the InterParserQueue to send to the specific queue
            if type(data) == dict: #Every interparser communication must be in a dict for easier use
                for i in self.parser_list:
                    if i == data['to']: #Try to get the corresponding parser
                        try:
                            self.parser_list[i]['interparserqueue'].put(data) #Finally, put the data for processing in the parser
                            break
                        except:
                            logger.fatal("Couldn't find {} Queue".format(i))
                else:
                    logger.fatal("Couldn't find {} parser in parserlist".format(data['to']))
            else:
                logger.error("Every Parser communication must be a dict and not a {}".format(type(data)))

    def InitializeAllParsers(self):
        for e in self.parser_list:
            if variables.typee == self.parser_list[e]["type"] or self.parser_list[e]["type"] == "": #Check if parser matches the current type
                needed_args = [] 
                for i in self._kwargs: #Get all arguments needed for initializing the parser
                    if i in self.parser_list[e]['args']:
                        needed_args.append(self._kwargs[i])
                parserq = queue.Queue()
                self.parser_list[e]["interparserqueue"] = parserq
                needed_args.append(parserq) #Append interparserqueue at the end, it is needed to communicate with every parser
                logging.info("Trying to initialize {} parser".format(e))
                self.parser_list[e]['initobj'] = self.parser_list[e]['obj'](*needed_args) #Try to initialize the parser
                logging.info("Initialized sucessfully {} parser".format(e))
                self.parser_list[e]['active'] = True

    def InitializeOneParser(self, name):
        for r in self.parser_list:
            if r == name:
                if self.parser_list[r]['type'] != variables.typee or self.parser_list[r]["type"] != "": #Check if the types match to avoid caotic stuff
                    logging.fatal("{} it's not of the same type.\n\tCarnotaurus is running in : {} \n\t Required Type: {} , aborting..".format(r, variables.typee, self.parser_list[r]['type']))
                    break
                else:
                    needed_args = [] 
                    for i in self._kwargs: #Get all arguments needed for initializing the parser
                        if i in self.parser_list[r]['args']:
                            needed_args.append(self._kwargs[i])
                    if self.parser_list[r]['active'] != True: #Check if parser is already running
                        logging.info("Trying to initialize {} parser".format(r))
                        self.parser_list[r]['initobj'] = self.parser_list[r]['obj'](*needed_args) #Try to initialize the parser
                        logging.info("Initialized sucessfully {} parser".format(r))
                        self.parser_list[r]['active'] = True
                    else:
                        logger.debug("{} is already running.".format(name))
                    break
        else:
            logging.debug("{} wasn't found in parser list.".format(name))
    
    def AddArgument(self, argname, argument):
        if type(argname) == str: #Check if argname is a string because keys must be a string
            for i in self._kwargs: #Check If Argument exists, if it does it will not add it to the argument dict
                if argname == i:
                    return
            self._kwargs[argname] = argument
        else:
            logger.fatal("Argname must be a str and not a {}".format(argname))
            return