import pickle
import unittest

from tests.testutil import TestUtil
from vr900connector.util import FileUtils


class FileUtilsTest(unittest.TestCase):

    def test_load_from_file_not_exists(self):
        path = TestUtil.temp_path()
        result = FileUtils.load_from_file(path, 'test_load_from_file.txt')
        self.assertIsNone(result)

    def test_load_from_file_exists(self):
        path = TestUtil.temp_path()
        file = 'test_load_from_file.txt'
        data = bytes('test data', 'utf-8')

        with open(path + '/' + file, 'wb+') as f:
            pickle.dump(data, f)

        result = FileUtils.load_from_file(path, file)
        self.assertEqual(data, result)

    def test_save_to_file_exists(self):
        path = TestUtil.temp_path()
        file = 'test_save_to_file.txt'
        data = bytes('test data', 'utf-8')

        with open(path + '/' + file, 'wb+'):
            pass

        FileUtils.save_to_file(data, path, file)

        with open(path + '/' + file, 'rb') as f:
            self.assertEqual(data, pickle.load(f))

    def test_save_to_file_not_exists(self):
        path = TestUtil.temp_path()
        file = 'test_save_to_file.txt'
        data = bytes('test data', 'utf-8')

        FileUtils.save_to_file(data, path, file)

        with open(path + '/' + file, 'rb') as f:
            self.assertEqual(data, pickle.load(f))
