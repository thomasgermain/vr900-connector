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
ROOMS_URL = "/facilities/{serialNumber}/rbr/v1/rooms"
ROOM_TIMEPROGRAM_URL = "/facilities/{serialNumber}/rbr/v1/rooms/{index}/timeprogram"
ZONES_URL = "/facilities/{serialNumber}/systemcontrol/v1/zones"
DHW_URL = "/facilities/{serialNumber}/systemcontrol/v1/dhw/{id}/hotwater"
DHW_SETPOINT_TEMPERATURE_URL = DHW_URL + '/configuration/temperature_setpoint'
DHW_SET_OPERATION_MODE_URL = DHW_URL + '/configuration/operation_mode'
CIRCULATION_URL = "/facilities/{serialNumber}/systemcontrol/v1/dhw/{id}/circulation"
HVAC_STATE_URL = "/facilities/{serialNumber}/hvacstate/v1/overview"
SYSTEM_STATUS_URL = "/facilities/{serialNumber}/system/v1/status"
SYSTEM_CONTROL_URL = "/facilities/{serialNumber}/systemcontrol/v1"
LIVE_REPORT_URL = "/facilities/{serialNumber}/livereport/v1"
QUICK_MODE_URL = SYSTEM_CONTROL_URL + "/configuration/quickmode"
CURRENT_PV_METERING_INFO_URL = '/facilities/{serialNumber}/spine/v1/currentPVMeteringInfo'
EMF_URL = '/facilities/{serialNumber}/emf/v1/devices'
REPEATERS_URL = '/facilities/{serialNumber}/rbr/v1/repeaters'
