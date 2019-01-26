import tempfile

DEFAULT_FILES_DIR = tempfile.gettempdir() + "/vaillant_vr900_files"

DEFAULT_COOKIE_FILE_NAME = "/.vr900-vaillant.cookies"
DEFAULT_SERIAL_NUMBER_FILE_NAME = "/.vr900-vaillant.serial"

DEFAULT_SMARTPHONE_ID = "vr900-connector"

DEFAULT_BASE_URL = "https://smart.vaillant.com/mobile/api/v4"
TEST_LOGIN_URL = "/account/user/v1/details"
REQUEST_NEW_TOKEN_URL = "/account/authentication/v1/token/new"
AUTHENTICATE_URL = "/account/authentication/v1/authenticate"

FACILITIES_URL = "/facilities"
ROOMS_URl = "/facilities/{serialNumber}/rbr/v1/rooms"
ROOM_TIMEPROGRAM_URL = "/facilities/{serialNumber}/rbr/v1/rooms/{index}/timeprogram"
ZONES_URL = "/facilities/{serialNumber}/systemcontrol/v1/zones"
DHW_URL = "/facilities/{serialNumber}/systemcontrol/v1/dhw/{id}/hotwater"
DHW_SETPOINT_TEMPERATURE_URL = DHW_URL + '/configuration/temperature_setpoint'
CIRCULATION_URL = "/facilities/{serialNumber}/systemcontrol/v1/dhw/{id}/circulation"
HVAC_STATE_URL = "/facilities/{serialNumber}/hvacstate/v1/overview"
SYSTEM_STATUS_URL = "/facilities/{serialNumber}/system/v1/status"
SYSTEM_CONTROL_URL = "/facilities/{serialNumber}/systemcontrol/v1"
LIVE_REPORT_URL = "/facilities/{serialNumber}/livereport/v1"

WATER_HEATER_MODE_AUTO = 'AUTO'
WATER_HEATER_MODE_AUTO_OFF = 'AUTO_OFF'
WATER_HEATER_MODE_AUTO_ON = 'AUTO_ON'
WATER_HEATER_MODE_OFF = 'OFF'
WATER_HEATER_MODE_ON = 'ON'
WATER_HEATER_MODE_BOOST = 'QM_HOTWATER_BOOST'
WATER_HEATER_MODES = [WATER_HEATER_MODE_ON, WATER_HEATER_MODE_OFF, WATER_HEATER_MODE_BOOST]

WATER_HEATER_MIN_TEMP = 35
WATER_HEATER_MAX_TEMP = 70
