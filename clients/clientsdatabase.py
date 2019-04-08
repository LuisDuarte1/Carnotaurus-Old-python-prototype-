import sqlite3
import logging
import os

logger = logging.getLogger(__name__)

class ClientDatabase:

    def __init__(self, path):
        dbexists = False
        if os.path.isfile(path): #Check if database exists
            dbexists = True
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()
        if dbexists == False: #If database dosen't exist create a new table to store client infos
            self.cursor.execute('''CREATE TABLE "clients" (
                        "UUID"	TEXT NOT NULL UNIQUE,
                        "Specs"	TEXT,
                        "Name"	TEXT
                    );''')

    def AddClient(self, uuid):
        if type(uuid) == str: #UUID must be a string to add to the database
            try:
                self.cursor.execute('''
                        INSERT INTO 'clients' VALUES (?, NULL, NULL);
                        ''', (uuid,))
            except sqlite3.IntegrityError: #UUID must be unique to avoid collisions 
                logger.fatal("This UUID ({}) already exists in database".format(uuid))
                return
            self.conn.commit()
        else:
            raise TypeError("UUID must be a str and not a {}".format(type(uuid)))
    
    def CheckIfUUIDExists(self, uuid):
        if type(uuid) == str:
            self.cursor.execute('''
                        SELECT EXISTS (SELECT * FROM "clients" WHERE UUID=?)
                    ''', (uuid,))
            if self.cursor.fetchone() == (1,): #Get the value from the query above and return in it's true or false
                return True
            else:
                return False
        else:
           raise TypeError("UUID must be a str and not a {}".format(type(uuid))) 


c = ClientDatabase("clients.db")
print(c.CheckIfUUIDExists("helao"))