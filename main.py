import networking
import logging
import config
import argparse
import parsers
import variables


def GetArguments():
    parser = argparse.ArgumentParser() 
    parser.add_argument("--debug", help="Turns on debug mode. Be careful debug it may output some confidential data", action="store_true") #Add optional debug argument
    parser.add_argument("--server", help="Start Carnotaurus as the master server. This will change the config", action="store_true") #Add server option
    parser.add_argument("--client", help="Start Carnotaurus as a node. This will change the config", action="store_true") #Add client option
    parser.add_argument("--output_log", help="Create a log file instead of outputting to STDOUT", type=str)
    return parser.parse_args() #return all arguments

def GetModeChange(args, c):
    if args.server == True and args.client == True: #Check if -- server and --client are used at the same time
        logging.fatal("Can't use --server and --client at the same time. Exiting..")
        exit(1)
    elif args.server == False and args.client == False: #Check if they aren't used and continue to load Carnotaurus normally
        return
    elif args.server == True:
        logging.debug("Changing Carnotaurus to server mode")
        c.ChangeConfigArgument("mode", "server")
    elif args.client == True:
        logging.debug("Changing Carnotaurus to node mode")
        c.ChangeConfigArgument("mode", "client")

def MainServer():
    variables.typee = "SERVER"
    logging.info("Initializing TCP server...")
    netserver = networking.TcpServer("0.0.0.0", 12134) #Initialize the tcp server to listen to all nodes 
    logging.info("Done initializing TCP server.")
    logging.info("Trying to initialize Parser Pool..")
    parsers.ParserPool(mainqueuerecv = netserver.mainqueuerecv, mainqueuesend = netserver.mainqueuesend)
    logging.info("Done initializing Parser Pool..")

def MainClient():
    logging.info("Trying to connect to the server..")
    client = networking.TcpClient("127.0.0.1", 12134)
    logging.info("Trying to initialize Parser Pool..")
    parsers.ParserPool(mainqueuerecv = client.mainqueuerecv, mainqueuesend = client.mainqueuesend)
    logging.info("Done initializing Parser Pool..")
    
def StartLogging(debug, output_log):
    if debug == True:
        if output_log is not None: #check if output log was requested in the args
            logging.basicConfig(format="[%(module)s] at %(asctime)s: %(levelname)s: %(message)s", level=logging.DEBUG, filename=output_log)
        else:
            logging.basicConfig(format="[%(module)s] at %(asctime)s: %(levelname)s: %(message)s", level=logging.DEBUG)
    else:
        if output_log is not None:
            logging.basicConfig(format="[%(module)s] at %(asctime)s: %(levelname)s: %(message)s", level=logging.INFO, filename=output_log)
        else:
            logging.basicConfig(format="[%(module)s] at %(asctime)s: %(levelname)s: %(message)s", level=logging.INFO)
          
if __name__ == "__main__":
    args = GetArguments()
    StartLogging(args.debug, args.output_log)
    c = config.MainConfig()
    GetModeChange(args, c)
    if c.GetConfigArgument("mode") == "server":
        MainServer()
    else:
        MainClient()