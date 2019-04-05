import tempfile


class Defaults:
    """
    This contains some default parameters of the application
    """

    FILES_PATH = tempfile.gettempdir() + '/.vaillant_vr900_files'

    COOKIE_FILE_NAME = '.vr900-vaillant.cookies'
    SERIAL_NUMBER_FILE_NAME = '.vr900-vaillant.serial'

    SMART_PHONE_ID = 'vr900-connector'
