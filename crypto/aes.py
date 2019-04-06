import logging
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import json
from math import ceil
import base64

logging.getLogger(__name__)

class AES:

    def __init__(self, create_key=True):
        if create_key == True:
            self.key = os.urandom(32) #Generate a random key
            self.iv = os.urandom(16)
            self.cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=default_backend()) #Using cryptography AES 
            self.encryptor = self.cipher.encryptor()
            self.decryptor = self.cipher.decryptor()
        else:
            self.key = None
            self.iv = None
            self.cipher = None

    def Encrypt(self, message): #Encrypt message if only the message is in bytes and if the cipher is initialized 
        if type(message) == bytes:
            if self.cipher != None:
                self.encryptor = self.cipher.encryptor()
                total_bytes_needed = (ceil(len(message) / 16) * 16) - len(message)
                message += b"\0"*total_bytes_needed
                return self.encryptor.update(message) + self.encryptor.finalize()
            else:
                logging.fatal("Tried to encrypt a message while AES wasn't fully initialized")
        else:
            raise TypeError("The message must be in bytes and not in {}".format(type(message)))

    def Decrypt(self, ciphertext):
        if type(ciphertext) == bytes:
            if self.cipher != None:
                self.decryptor = self.cipher.decryptor()
                return (self.decryptor.update(ciphertext) + self.decryptor.finalize()).split(b'\0',1)[0]
            else:
                logging.fatal("Tried to decrypt a message while AES wasn't fully initialized")
        else:
            raise TypeError("The ciphertext must be in bytes and not in {}".format(type(ciphertext)))

    def GetKey(self):
        key = base64.b64encode(self.key).decode("utf-8")
        iv = base64.b64encode(self.iv).decode("utf-8")
        return json.dumps({'key': key, 'iv': iv , 'aesisfkncool':True}).encode("utf-8")
    
    def LoadKey(self, key):
        if type(key) == bytes:
            key_dict = json.loads(key.decode("utf-8")) #Load to a dictionary
            try:
                self.key = base64.b64decode(key_dict['key'].encode("utf-8")) 
                self.iv = base64.b64decode(key_dict['iv'].encode("utf-8"))
            except KeyError:
                raise TypeError("This key it isn't in a valid format.")
            self.cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=default_backend()) 
            self.encryptor = self.cipher.encryptor()
            self.decryptor = self.cipher.decryptor()
        else:
            raise TypeError("Key must be in bytes and not in {}".format(type(key))) 

