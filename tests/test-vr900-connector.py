import unittest
from connector import Vr900Connector


class TestVr900Connector(unittest.TestCase):

    def testConnect(self):
        connector = Vr900Connector('', '')
        connector.login()


if __name__ == '__main__':
    unittest.main()
