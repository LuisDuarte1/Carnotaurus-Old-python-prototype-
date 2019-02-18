import os.path
import json
import logging

logger = logging.getLogger(__name__) #Get logger from main 

class MainConfig:

    def __init__(self):
        if os.path.isfile("config.json") == False:
            self.FirstRun()
        self.LoadConfig()

    def FirstRun(self):
        with open("config.json", "w") as f: #Open the config file, overriding if the config already exists
            configdict = {}
            configdict['mode'] = 'client' #Set carnotaurus as client by default, you can change this by using the argument --server
            f.write(json.dumps(configdict))

    def LoadConfig(self):
        self.configdict = json.load(open("config.json", "r")) #Get dict by using json.load because it does the transformation between string and dict
    
    def GetConfigArgument(self, key):
        try:
            return self.configdict[key]
        except Exception as e:
            logger.fatal(e) #Log the exception

    def ChangeConfigArgument(self, key, value):
        try:
            self.configdict[key] = value 
            self.CommitToConfigFile()
        except Exception as e:
            logger.fatal(e) #Log the exception
    

    def CommitToConfigFile(self):
        with open("config.json", "w") as f: #This will override the old config 
            f.write(json.dumps(self.configdict))