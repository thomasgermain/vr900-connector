import json
import unittest
import inspect
from vr900connector.api.payloads import Payloads


class PayloadsTest(unittest.TestCase):

    def test_all_payload(self):
        functions_list = inspect.getmembers(Payloads, predicate=inspect.ismethod)

        self.assertTrue(len(functions_list) > 0)

        for function in functions_list:
            args_name = self._get_args_name(function[1])

            if len(args_name) == 0:
                url = function[1]()
                self._assert_function_call(url)
            else:
                args = []
                for i in range(len(args_name)):
                    args.append('test')

                f_kwargs = dict(zip(args_name, args))
                payload = function[1](**f_kwargs)
                self._assert_function_call(payload)

    def _get_args_name(self, function):
        names = []
        for item in inspect.signature(function).parameters.items():
            names.append(item[0])
        return names

    def _assert_function_call(self, result):
        json.loads(json.dumps(result))


if __name__ == '__main__':
    unittest.main()
