import tempfile

DEFAULT_COOKIE_LOCATION = tempfile.gettempdir() + '/vaillant_vr900_cookies'

DEFAULT_SMARTPHONE_ID = 'vr900-connector'

DEFAULT_BASE_URL = 'https://smart.vaillant.com/mobile/api/v4'
REQUEST_NEW_TOKEN_URL = '/account/authentication/v1/token/new'
AUTHENTICATE_URL = '/account/authentication/v1/authenticate'
FACILITIES = '/facilities'
