import os


class TestUtil:

    @staticmethod
    def path(file):
        return os.path.join(os.path.dirname(__file__), file)
