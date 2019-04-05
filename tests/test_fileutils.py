import os
import pickle
import unittest
from unittest.mock import Mock, patch

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

    @patch.object(pickle, 'dump')
    def test_save_to_file_no_error_on_exception(self, mock_dump):
        path = TestUtil.temp_path()
        file = 'test_save_to_file.txt'
        data = bytes('test data', 'utf-8')

        mock_dump.side_effect = Exception('Test exception')

        FileUtils.save_to_file(data, path, file)

        self.assertEqual(0, os.stat(os.path.join(path, file)).st_size)

    def test_delete_dir(self):
        path = TestUtil.temp_path()
        self.assertTrue(os.path.exists(path))
        FileUtils.delete_dir(path)
        self.assertFalse(os.path.exists(path))

    def test_delete_dir_exception(self):
        path = TestUtil.temp_path()
        self.assertTrue(os.path.exists(path))
        os.rmdir = Mock(side_effect=Exception('Test exception'))
        FileUtils.delete_dir(path)
        self.assertTrue(os.path.exists(path))


if __name__ == '__main__':
    unittest.main()
