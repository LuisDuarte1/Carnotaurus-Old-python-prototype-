import logging
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

logger = logging.getLogger(__name__)

class RSA:

    def __init__(self, create_key=True):
        if create_key == True:
            self.only_public = False
            self._private_key = rsa.generate_private_key(65537, 2048, default_backend())
            self.public_key = self._private_key.public_key()
        else:
            self.only_public = True
            self.public_key = None  #Initializes public key as None for it to be Loaded

    def Encrypt(self, message):
        if self.public_key != None:
            if type(message) is bytes:
                return self.public_key.encrypt(message, padding.OAEP(padding.MGF1(hashes.SHA256()), hashes.SHA256(), label=None))
            else:
                raise TypeError("This message was of type {} and not bytes.".format(type(message)))
        else:
            logger.fatal("Can't encrypt message because a public key wasn't loaded")
    
    def Decrypt(self, ciphertext):
        if self.only_public == False:
            if type(ciphertext) is bytes:
                return self._private_key.decrypt(ciphertext, padding.OAEP(padding.MGF1(hashes.SHA256()), hashes.SHA256(), None))
            else:
                raise TypeError("This ciphertext was of type {} and not bytes.".format(type(ciphertext)))
    
    def LoadPublicKey(self, pem_data):
        if self.public_key == None:
            self.public_key = serialization.load_pem_public_key(pem_data, default_backend())
        else:
            logger.warning("A public key is already loaded.")

    def GetPublicKey(self):
        if self.public_key != None:
            return self.public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)
        else:
            logger.fatal("Can't encrypt message because a public key wasn't loaded")