import os.path
import json
import uuid
import logging
import sys
sys.path.append('../')
import variables

logger = logging.getLogger(__name__) #Get logger from main 

class MainConfig:

    def __init__(self, path="config.json"):
        self.path = path
        if os.path.isfile(path) == False:
            self.FirstRun()
        self.LoadConfig()
        variables.config_obj = self

    def FirstRun(self):
        with open(self.path, "w") as f: #Open the config file, overriding if the config already exists
            configdict = {}
            configdict['mode'] = 'client' #Set carnotaurus as client by default, you can change this by using the argument --server
            configdict['uuid'] = str(uuid.uuid4()) #Create a new uuid for this carnotaurs client/server
            f.write(json.dumps(configdict))

    def LoadConfig(self):
        self.configdict = json.load(open(self.path, "r")) #Get dict by using json.load because it does the transformation between string and dict
    
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
        with open(self.path, "w") as f: #This will override the old config 
            f.write(json.dumps(self.configdict))