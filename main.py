import networking
import logging
import argparse

def GetArguments():
    parser = argparse.ArgumentParser() 
    parser.add_argument("--debug", help="Turns on debug mode. Be careful debug it may output some confidential data", action="store_true") #Add optional debug argument
    parser.add_argument("--server", help="Start Carnotaurus as the master server. Carnotaurus starts from ", action="store_true") #Add server or client option
    return parser.parse_args() #return all arguments


def StartLogging(debug):
    if debug == True:
        logging.basicConfig(format="[%(module)s] at %(asctime)s: %(levelname)s: %(message)s", level=logging.DEBUG)
    else:
        logging.basicConfig(format="[%(module)s] at %(asctime)s: %(levelname)s: %(message)s", level=logging.INFO)

if __name__ == "__main__":
    args = GetArguments()
    StartLogging(args.debug)
    logging.info("Initializing TCP server...")
    netserver = networking.TcpServer("0.0.0.0", 12134) #Initialize the tcp server to listen to all nodes 
    logging.info("Done initializing TCP server.")
    logging.info("Initializing Parser...")
    ps = networking.TcpParser(netserver.mainqueuerecv, netserver.mainqueuesend)
    logging.info("Done initializing Parser.")