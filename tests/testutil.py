import os
import tempfile
import uuid


class TestUtil:

    @staticmethod
    def path(file):
        return os.path.join(os.path.dirname(__file__), file)

    @staticmethod
    def temp_path():
        return tempfile.gettempdir() + "/" + str(uuid.uuid4())
