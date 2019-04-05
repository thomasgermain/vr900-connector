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

        except Exception:
            _LOGGER.debug("Cannot open file: %s", join_path, exc_info=True)
            return None

    @classmethod
    def save_to_file(cls, data: any, path: str, filename:str):
        join_path = cls._join_path(path, filename)
        _LOGGER.debug("Will save data to %s", join_path)
        try:

            with join_path.open("wb+") as f:
                pickle.dump(data, f)

        except Exception:
            _LOGGER.debug("Cannot save data: %s to %s", str(data), join_path, exc_info=True)

    @classmethod
    def delete_file(cls, path: str, filename: str):
        join_path = cls._join_path(path, filename)
        try:
            os.remove(str(join_path))
        except Exception:
            _LOGGER.debug("Cannot delete file %s", join_path, exc_info=True)

    @classmethod
    def delete_dir(cls, path: str):
        try:
            os.rmdir(path)
        except Exception as e:
            _LOGGER.debug("Cannot delete dir %s", path, exc_info=True)

    @classmethod
    def _join_path(cls, path: str, filename: str):
        file_path = Path(path)
        file_path.mkdir(exist_ok=True, parents=True)
        return file_path.joinpath(filename)
