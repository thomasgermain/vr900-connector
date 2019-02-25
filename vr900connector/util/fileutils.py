import logging
import os
import pickle
from pathlib import Path

_LOGGER = logging.getLogger('FileUtils')


class FileUtils:

    @classmethod
    def load_from_file(cls, path: str, filename: str):
        join_path = cls._join_path(path, filename)
        try:
            with join_path.open("rb") as f:
                return pickle.load(f)

        except IOError:
            _LOGGER.debug("File %s not found", join_path)
            return None
        except Exception as e:
            _LOGGER.error("Cannot open file: %s", join_path)
            raise e

    @classmethod
    def save_to_file(cls, data: any, path: str, filename:str):
        join_path = cls._join_path(path, filename)
        _LOGGER.debug("Will save data to %s", join_path)
        try:

            with join_path.open("wb+") as f:
                pickle.dump(data, f)

        except Exception as e:
            _LOGGER.error("Cannot save data: %s to %s", str(data), join_path)
            raise e

    @classmethod
    def delete_file(cls, path: str, filename: str):
        join_path = cls._join_path(path, filename)
        try:
            os.remove(join_path)
        except Exception as e:
            _LOGGER.exception("Cannot delete file %s", join_path, e)

    @classmethod
    def delete_dir(cls, path: str):
        try:
            os.rmdir(path)
        except Exception as e:
            _LOGGER.exception("Cannot delete dir %s", path, e)

    @classmethod
    def _join_path(cls, path: str, filename: str):
        file_path = Path(path)
        file_path.mkdir(exist_ok=True)
        return file_path.joinpath(filename)
