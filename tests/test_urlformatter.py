import unittest

from vr900connector.util import UrlFormatter


class UrlFormatterTest(unittest.TestCase):

    def test_format_no_params_no_supplied(self):
        formatted = UrlFormatter.format('bouh')
        self.assertEqual('bouh', formatted)

    def test_format_no_params_some_supplied(self):
        formatted = UrlFormatter.format('bouh', serial='123')
        self.assertEqual('bouh', formatted)

    def test_format_missing_param_not_safe(self):
        try:
            UrlFormatter.format('$serialNumber', safe=False)
            self.fail('Error expected')
        except KeyError as e:
            self.assertEqual('serialNumber', e.args[0])

    def test_format_missing_param_safe(self):
        formatted = UrlFormatter.format('$serialNumber')
        self.assertEqual(formatted, '$serialNumber')

    def test_format_params_mismatch(self):
        formatted = UrlFormatter.format('$test', serial='123')
        self.assertEqual(formatted, '$test')
