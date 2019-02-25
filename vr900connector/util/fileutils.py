import logging
import os
import pickle
from pathlib import Path

_LOGGER = logging.getLogger('FileUtils')


class FileUtils:

    @classmethod
    def load_from_file(cls, path, filename):
        join_path = cls._join_path(path, filename)
        try:
            with join_path.open("rb") as f:
                return pickle.load(f)

        except IOError:
            _LOGGER.debug("File %s not found", join_path)
            return None
        except Exception as e:
            _LOGGER.exception("Cannot open file: %s", join_path)
            raise e

    @classmethod
    def save_to_file(cls, data, path, filename):
        join_path = cls._join_path(path, filename)
        _LOGGER.debug("Will save data to %s", join_path)
        try:

            with join_path.open("wb+") as f:
                pickle.dump(data, f)

        except Exception as e:
            _LOGGER.exception("Cannot save data: %s to %s", str(data), join_path)
            raise e

    @classmethod
    def delete_file(cls, path, filename):
        join_path = cls._join_path(path, filename)
        try:
            os.remove(join_path)
        except Exception as e:
            _LOGGER.debug("Cannot delete file %s", join_path)

    @classmethod
    def delete_dir(cls, path):
        try:
            os.rmdir(path)
        except Exception as e:
            _LOGGER.debug("Cannot delete dir %s", path)

    @classmethod
    def _join_path(cls, path, filename):
        file_path = Path(path)
        file_path.mkdir(exist_ok=True)
        return file_path.joinpath(filename)
