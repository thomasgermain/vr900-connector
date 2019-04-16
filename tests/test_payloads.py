import json
import unittest
import inspect
from datetime import datetime

from vr900connector.api.payloads import Payloads


class PayloadsTest(unittest.TestCase):

    def test_all_payload(self):
        functions_list = inspect.getmembers(Payloads, predicate=inspect.ismethod)

        self.assertTrue(len(functions_list) > 0)

        for function in functions_list:
            args = self._get_args_name(function[1])

            if len(args) == 0:
                url = function[1]()
                self._assert_function_call(url)
            else:
                payload = function[1](**args)
                self._assert_function_call(payload)

    def _get_args_name(self, function):
        args = {}
        params = inspect.signature(function).parameters

        for item in inspect.signature(function).parameters.items():
            cls = params[item[0]].annotation

            if cls.__name__ == 'bool':
                args[item[0]] = False
            elif cls.__name__ == 'float':
                args[item[0]] = 10.0
            elif cls.__name__ == 'date':
                args[item[0]] = datetime.now()
            elif cls.__name__ == 'str':
                args[item[0]] = 'test'
            elif cls.__name__ == 'int':
                args[item[0]] = 10
            else:
                self.fail("Unhandled class " + cls.__name__)

        return args

    def _assert_function_call(self, result):
        json.loads(json.dumps(result))


if __name__ == '__main__':
    unittest.main()
