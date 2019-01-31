import logging
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

logger = logging.getLogger(__name__)

class RSA:

    def __init__(self, create_key=True):
        if create_key == True:
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
