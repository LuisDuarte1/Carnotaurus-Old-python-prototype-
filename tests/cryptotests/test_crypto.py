import unittest
import random
import string
import sys
sys.path.append('../')
import crypto

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

class Test_AES(unittest.TestCase):
    
    def test_aes(self):
        c = crypto.AES()
        randstring = randomString().encode("utf-8")
        ciphertext = c.Encrypt(randstring)
        self.assertEqual(c.Decrypt(ciphertext), randstring)

    def test_aes_key_passing(self):
        c = crypto.AES()
        s = crypto.AES(False)
        key = c.GetKey()
        s.LoadKey(key)
        randstring = randomString().encode("utf-8")
        ciphertext = c.Encrypt(randstring)
        self.assertEqual(s.Decrypt(ciphertext), randstring)
    
    def test_aes_encrypt_bytes_only(self):
        c = crypto.AES()
        with self.assertRaises(TypeError):
            c.Encrypt(randomString())

    def test_aes_decrypt_bytes_only(self):
        c = crypto.AES()
        with self.assertRaises(TypeError):
            c.Decrypt(randomString())

class Test_RSA(unittest.TestCase):

    def test_rsa(self):
        r = crypto.RSA()
        randstring = randomString().encode("utf-8")
        ciphertext = r.Encrypt(randstring)
        self.assertEqual(r.Decrypt(ciphertext), randstring)
    
    def test_rsa_keypassing(self):
        r = crypto.RSA()
        s = crypto.RSA(False)
        key = r.GetPublicKey()
        s.LoadPublicKey(key)
        randstring = randomString().encode("utf-8")
        ciphertext = s.Encrypt(randstring)
        self.assertEqual(r.Decrypt(ciphertext), randstring)
    
    def test_rsa_dont_decrypt_when_public_key_only(self):
        r = crypto.RSA(False)
        self.assertEqual(r.Decrypt(randomString().encode("utf-8")), None)
    
    def test_rsa_encrypt_only_bytes(self):
        r = crypto.RSA()
        with self.assertRaises(TypeError):
            r.Encrypt(randomString())
    
    def test_rsa_decrypt_only_bytes(self):
        r = crypto.RSA()
        with self.assertRaises(TypeError):
            r.Decrypt(randomString())

if __name__ == '__main__':
    unittest.main()