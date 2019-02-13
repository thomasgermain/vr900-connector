import requests
import logging

from ..util import FileUtils, UrlFormatter
from . import ApiError
from . import constant

LOGGER = logging.getLogger('Connector')


class ApiConnector:
    """
    This is the low level smart.vaillant.com API connector.
    This connector is handling some part of the API as well as the login.
    For now, only some GET part of the API are handled. It means you cannot alter data with this connector
    """

    def __init__(self, user, password, smart_phone_id=constant.DEFAULT_SMART_PHONE_ID,
                 base_url=constant.DEFAULT_BASE_URL, file_dir=constant.DEFAULT_FILES_DIR, auto_close_session=True):
        self.__user = user
        self.__password = password
        self.__smart_phone_Id = smart_phone_id
        self.__baseUrl = base_url
        self.__fileDir = file_dir
        self.__headers = {'content-type': 'application/json'}
        self.autoCloseSession = auto_close_session
        self.__serialNumber = self.__load_serial_number_from_file()
        self.__session = self.__create_session()

    def query(self, url, method='GET', payload=None):
        """
        url must be relative to base_url.
        Serial number can be provided if you put $serialNumber in url.
        """

        safe_url = url if url.startswith('/') else '/' + url
        return self.__secure_call(method, safe_url, payload)

    def get(self, url):
        return self.query(url)

    def put(self, url, payload=None):
        return self.query(url, 'PUT', payload)

    def post(self, url, payload=None):
        return self.query(url, 'POST', payload)

    def delete(self, url):
        return self.query(url, 'DELETE')

    def get_current_pv_metering_inf(self):
        return self.get(constant.CURRENT_PV_METERING_INFO_URL)

    def get_emf(self):
        return self.get(constant.EMF_URL)

    def get_repeaters(self):
        return self.get(constant.REPEATERS_URL)

    def get_facilities(self):
        return self.get(constant.FACILITIES_URL)

    def get_live_report(self):
        return self.get(constant.LIVE_REPORT_URL)

    def get_system_status(self):
        return self.get(constant.SYSTEM_STATUS_URL)

    def get_hvac_state(self):
        return self.get(constant.HVAC_STATE_URL)

    def get_rooms(self):
        return self.get(constant.ROOMS_URL)

    def get_system_control(self):
        return self.get(constant.SYSTEM_CONTROL_URL)

    def get_zones(self):
        return self.get(constant.ZONES_URL)

    def get_room(self, index):
        return self.get(UrlFormatter.format(constant.ROOM_URL, room=str(index)))

    def get_zone(self, zone_id):
        return self.get(UrlFormatter.format(constant.ZONE_URL, zone=str(zone_id)))

    def get_dhw(self):
        return self.get(self.__baseUrl + constant.DHW_URL)

    def get_circulation(self, dhw_id):
        return self.get(UrlFormatter.format(constant.DHW_CIRCULATION_URL, dhw=str(dhw_id)))

    def get_hotwater(self, dhw_id):
        return self.get(UrlFormatter.format(constant.DHW_HOTWATER_URL, dhw=str(dhw_id)))

    def set_hotwater_setpoint_temperature(self, dhw_id, temperature):
        return self.__secure_call('PUT',
                                  UrlFormatter.format(constant.DHW_HOTWATER_SET_POINT_TEMPERATURE_URL, dhw=str(dhw_id)),
                                  {'temperature_setpoint': temperature})

    def set_hotwater_operation_mode(self, dhw_id, mode):
        return self.__secure_call('PUT',
                                  UrlFormatter.format(constant.DHW_HOTWATER_OPERATION_MODE_URL, dhw=str(dhw_id)),
                                  {"operation_mode": mode})

    def remove_quick_mode(self):
        return self.__secure_call('DELETE', constant.SYSTEM_QUICK_MODE_URL)

    def set_quick_mode(self, mode, duration=None):
        """Duration in minutes, most of the time, the duration will be overridden by vaillant"""

        payload = {
            "quickmode":
                {
                    "quickmode": str(mode),
                    "duration": duration if duration is not None else 0
                }
        }
        return self.__secure_call('PUT', constant.SYSTEM_QUICK_MODE_URL, payload=payload)

    def logout(self):
        self.__session.request('POST', constant.LOGOUT_URL)
        self.close_session(True)

    def close_session(self, clear=False):
        LOGGER.debug('Closing session')
        self.__session.close()
        if clear:
            self.__clear_session()
            FileUtils.delete_dir(self.__fileDir)

    def __secure_call(self, method, url, payload=None, re_login=False):
        response = None
        safe_url = None
        try:
            self.__login(re_login)

            safe_url = self.__baseUrl + UrlFormatter.format(url, serial=self.__serialNumber)
            response = self.__session.request(method, safe_url, json=payload,
                                              headers=None if payload is None else self.__headers)

            if response.status_code > 399:
                if not re_login and response.status_code == 401:
                    LOGGER.debug('Call to %s failed with HTTP 401, will try to re-login')
                    """Try to re-login"""
                    self.__secure_call(method, url, payload, True)
                else:
                    raise ApiError('Received error from server url: ' + safe_url + ' and method ' + method, response)
            if response.text:
                return response.json()
            else:
                return {"ok": "ok"}
        except ApiError:
            LOGGER.error('Cannot %s url: %s', method, safe_url if safe_url else url)
            raise
        except Exception as e:
            LOGGER.exception('Cannot %s url: %s', method, safe_url if safe_url else url)
            raise ApiError(str(e), response)
        finally:
            if self.autoCloseSession:
                self.close_session()

    def __login(self, re_login=False):
        try:
            if re_login:
                self.__clear_session()
            if not self.__session.cookies:
                self.__session = self.__create_session()

                if not self.__session.cookies:
                    LOGGER.info(
                        'No previous session found, will try to logging with username: %s and smartphoneId: %s to %s',
                        self.__user, self.__smart_phone_Id, self.__baseUrl)

                    authtoken = self.__request_token()
                    self.__get_cookies(authtoken)
                    self.__get_serial_number()
        except ApiError:
            raise
        except Exception as e:
            LOGGER.error('Error during logging', e)
            raise ApiError('Error during logging ' + str(e), None)

    def __request_token(self):
        params = {
            "smartphoneId": self.__smart_phone_Id,
            "username": self.__user,
            "password": self.__password
        }

        response = self.__session.post(self.__baseUrl + constant.REQUEST_NEW_TOKEN_URL,
                                       json=params, headers=self.__headers)
        if response.status_code == 200:
            LOGGER.debug('Token generation successful')
            auth_token = response.json()['body']['authToken']
            if not auth_token:
                raise ApiError('Generated token is empty', response)
            return auth_token
        else:
            raise ApiError('Authentication failed', response)

    def __get_cookies(self, authtoken):
        params = {
            "smartphoneId": self.__smart_phone_Id,
            "username": self.__user,
            "authToken": authtoken
        }
        response = self.__session.post(self.__baseUrl + constant.AUTHENTICATE_URL, json=params, headers=self.__headers)

        if response.status_code == 200:
            LOGGER.debug('Cookie successfully retrieved')
            self.__save_cookies_to_file()
        else:
            raise ApiError('Cannot get cookies', response)

    def __get_serial_number(self):
        response = self.__session.get(self.__baseUrl + constant.FACILITIES_URL)

        if response.status_code == 200:
            LOGGER.debug('Serial number successfully retrieved')
            self.__serialNumber = response.json()['body']['facilitiesList'][0]['serialNumber']
            self.__save_serial_number_to_file()
        else:
            raise ApiError('Cannot get serial number', response)

    def __test_login(self):
        return self.__session.get(self.__baseUrl + constant.TEST_LOGIN_URL)

    def __create_session(self):
        session = requests.session()
        cookies = self.__load_cookies_from_file()
        LOGGER.debug('Found cookies %s', cookies)
        if cookies is not None:
            session.cookies = cookies
        return session

    def __clear_session(self):
        self.__clear_cookie()
        self.__clear_serial_number()
        self.__session = requests.session()

    def __save_cookies_to_file(self):
        FileUtils.save_to_file(self.__session.cookies, constant.DEFAULT_COOKIE_FILE_NAME, self.__fileDir)

    def __save_serial_number_to_file(self):
        FileUtils.save_to_file(self.__serialNumber, constant.DEFAULT_SERIAL_NUMBER_FILE_NAME, self.__fileDir)

    def __load_cookies_from_file(self):
        return FileUtils.load_from_file(self.__fileDir + constant.DEFAULT_COOKIE_FILE_NAME)

    def __load_serial_number_from_file(self):
        return FileUtils.load_from_file(self.__fileDir + constant.DEFAULT_SERIAL_NUMBER_FILE_NAME)

    def __clear_cookie(self):
        FileUtils.delete_file(self.__fileDir + '/' + constant.DEFAULT_COOKIE_FILE_NAME)

    def __clear_serial_number(self):
        FileUtils.delete_file(self.__fileDir + '/' + constant.DEFAULT_SERIAL_NUMBER_FILE_NAME)
