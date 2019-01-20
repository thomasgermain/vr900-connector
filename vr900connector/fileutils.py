import os
import pickle
import logging

from . import constant

logger = logging.getLogger('FileUtils')


class FileUtils:
    @staticmethod
    def load_from_file(path):
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            logger.debug("File %s not found", path)
            return None
        except Exception as e:
            logger.error("Cannot open file: %s, error: %s", path, str(e))
            return None

    @staticmethod
    def save_to_file(data, filename, path=constant.DEFAULT_FILES_DIR):
        try:
            os.makedirs(path, exist_ok=True)
            with open(path + "/" + filename, "wb+") as f:
                pickle.dump(data, f)
        except Exception as e:
            logger.error("Cannot save data: %s file: %s, error: ", path + filename, data, str(e))

    @staticmethod
    def delete_file(path):
        os.remove(path)
