import sys
import os
sys.path.append('../')
import unittest
import config

class Test_MainConfig(unittest.TestCase):

    def test_writing_config(self):
        c = config.MainConfig(path="test_config_write.json")
        uuid = c.GetConfigArgument("uuid")
        d = config.MainConfig(path="test_config_write.json")
        uuid2 = c.GetConfigArgument("uuid")
        os.remove("test_config_write.json")
        self.assertEqual(uuid, uuid2)
    
    def test_reading_config(self):
        c = config.MainConfig(path="tests/configtests/test_config.json")
        self.assertEqual(c.GetConfigArgument("uuid"), "fec76711-56ee-4991-8bfd-1344fb70de34")