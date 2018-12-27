import unittest
import inspect

from vr900connector.api import Urls


class TestUrls(unittest.TestCase):

    def test_all_urls(self):
        functions_list = inspect.getmembers(Urls, predicate=inspect.ismethod)

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
                url = function[1](**f_kwargs)
                self._assert_function_call(url)

    def _get_args_name(self, function):
        names = []
        for item in inspect.signature(function).parameters.items():
            names.append(item[0])
        return names

    def _assert_function_call(self, url):
        clean_url = url.replace('{serial_number}', '')
        self.assertNotIn('{', clean_url)
        self.assertNotIn('}', clean_url)


if __name__ == '__main__':
    unittest.main()
