import os
import pickle
import logging

LOGGER = logging.getLogger('FileUtils')


class FileUtils:
    @staticmethod
    def load_from_file(path):
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            LOGGER.debug("File %s not found", path)
            return None
        except Exception as e:
            LOGGER.error("Cannot open file: %s, error: %s", path, str(e))
            return None

    @staticmethod
    def save_to_file(data, filename, path):
        try:
            os.makedirs(path, exist_ok=True)
            with open(path + "/" + filename, "wb+") as f:
                pickle.dump(data, f)
        except Exception as e:
            LOGGER.error("Cannot save data: %s file: %s, error: ", path + filename, data, str(e))

    @staticmethod
    def delete_file(path):
        try:
            os.remove(path)
        except Exception as e:
            LOGGER.debug("Cannot delete file %s, error: %s", path, str(e))

    @staticmethod
    def delete_dir(path):
        try:
            os.rmdir(path)
        except Exception as e:
            LOGGER.debug("Cannot delete dir %s, error: %s", path, str(e))
