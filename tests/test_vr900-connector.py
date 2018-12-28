import unittest
from vr900connector import Vr900Connector, Vr900ConnectorError


class TestVr900Connector(unittest.TestCase):

    def testConnect(self):
        connector = Vr900Connector('', '')

        try:
            data = connector.system_control()
            print(data)
        except Vr900ConnectorError as e:
            print(e)


if __name__ == '__main__':
    unittest.main()
