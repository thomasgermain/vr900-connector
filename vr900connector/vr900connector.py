from vr900connector import constant
from vr900connector.vr900connectorerror import Vr900ConnectorError
from vr900connector.fileutils import FileUtils
import requests
import logging

logger = logging.getLogger('Vr900Connector')

"""
This is the low level smart.vaillant.com API connector.
This connector is handling some part of the API as well as the login.
For now, only some GET part of the API are handled. It means you cannot alter data with this connector
"""


class Vr900Connector:

    def __init__(self, user, password, smartphone_id=constant.DEFAULT_SMARTPHONE_ID,
                 base_url=constant.DEFAULT_BASE_URL, file_dir=constant.DEFAULT_FILES_DIR):
        self.user = user
        self.password = password
        self.smartphoneId = smartphone_id
        self.baseUrl = base_url
        self.fileDir = file_dir
        self.headers = {"content-type": "application/json"}
        self.__serialNumber = self.__load_serial_number_from_file()
        self.__session = self.__create_session()

    def get_facilities(self):
        return self.__secure_call('GET', self.baseUrl + constant.FACILITIES_URL)

    def get_live_report(self):
        return self.__secure_call('GET', self.baseUrl + constant.LIVE_REPORT_URL)

    def get_system_status(self):
        return self.__secure_call('GET', self.baseUrl + constant.SYSTEM_STATUS_URL)

    def get_hvac_state(self):
        return self.__secure_call('GET', self.baseUrl + constant.HVAC_STATE_URL)

    def get_rooms(self):
        return self.__secure_call('GET', self.baseUrl + constant.ROOMS_URl)

    def get_room(self, index):
        return self.__secure_call('GET', self.baseUrl + constant.ROOMS_URl + "/" + str(index))

    def get_zones(self):
        return self.__secure_call('GET', self.baseUrl + constant.ZONES_URL)

    def get_system_control(self):
        return self.__secure_call('GET', self.baseUrl + constant.SYSTEM_CONTROL_URL)

    def __secure_call(self, method, url):
        response = None
        try:
            self.__login()
            url = url.replace("{serialNumber}", self.__serialNumber)
            response = self.__session.request(method, url)

            if response.status_code > 499:
                raise Vr900ConnectorError("Received error from server url: " + url + " and method " + method, response)
            return response.json()
        except Vr900ConnectorError:
            logger.error("Cannot %s url: %s", method, url)
            raise
        except Exception as e:
            logger.exception("Cannot %s url: %s", method, url)
            raise Vr900ConnectorError(str(e), response)
        finally:
            self.__close_session()

    def __login(self, relogin=False):
        try:
            if not self.__session.cookies:
                self.__session = self.__create_session()

                if not self.__session.cookies:
                    logger.info(
                        "No previous session found, will try to logging with username: %s and smartphoneId: %s to %s",
                        self.user, self.smartphoneId, self.baseUrl)

                    authtoken = self.__request_token()
                    self.__get_cookies(authtoken)
                    self.__get_serial_number()
            else:
                logger.debug(
                    "Session already exists, will test it...")
                testLoginResponse = self.__test_login()
                if testLoginResponse.status_code != 200:
                    if relogin:
                        raise Vr900ConnectorError("Logging test failed, relogin=" + str(relogin), testLoginResponse)
                    else:
                        logger.info("Cookie and serial files are outdated, re-logging")
                        self.__clear_session()
                        self.__login(True)
                else:
                    logger.debug("... session is ok")
        except Vr900ConnectorError:
            raise
        except Exception as e:
            logger.error("Error during logging", e)
            raise Vr900ConnectorError("Error during logging " + str(e), None)

    def __request_token(self):
        params = {
            "smartphoneId": self.smartphoneId,
            "username": self.user,
            "password": self.password
        }

        response = self.__session.post(self.baseUrl + constant.REQUEST_NEW_TOKEN_URL,
                                       json=params, headers=self.headers)
        if response.status_code == 200:
            logger.debug("Token generation successful")
            authtoken = response.json()["body"]["authToken"]
            if not authtoken:
                raise Vr900ConnectorError("Generated token is empty", response)
            return authtoken
        else:
            raise Vr900ConnectorError("Cannot generate token", response)

    def __get_cookies(self, authtoken):
        params = {
            "smartphoneId": self.smartphoneId,
            "username": self.user,
            "authToken": authtoken
        }
        response = self.__session.post(self.baseUrl + constant.AUTHENTICATE_URL, json=params, headers=self.headers)

        if response.status_code == 200:
            logger.debug("Cookie successfully retrieved")
            self.__save_cookies_to_file()
        else:
            raise Vr900ConnectorError("Cannot generate token", response)

    def __get_serial_number(self):
        response = self.__session.get(self.baseUrl + constant.FACILITIES_URL)

        if response.status_code == 200:
            logger.debug("Serial number successfully retrieved")
            self.__serialNumber = response.json()["body"]["facilitiesList"][0]["serialNumber"]
            self.__save_serial_number_to_file()
        else:
            raise Vr900ConnectorError("Cannot get serial number", response)

    def __test_login(self):
        return self.__session.get(self.baseUrl + constant.TEST_LOGIN_URL)

    def __create_session(self):
        session = requests.session()
        cookies = self.__load_cookies_from_file()
        logger.debug("Found cookies %s", cookies)
        if cookies is not None:
            session.cookies = cookies
        return session

    def __clear_session(self):
        self.__clear_cookie()
        self.__clear_serial_numbr()
        self.__session = requests.session()

    def __close_session(self):
        logger.debug("Closing session")
        self.__session.close()

    def __save_cookies_to_file(self):
        FileUtils.save_to_file(self.__session.cookies, constant.DEFAULT_COOKIE_FILE_NAME, self.fileDir)

    def __save_serial_number_to_file(self):
        FileUtils.save_to_file(self.__serialNumber, constant.DEFAULT_SERIAL_NUMBER_FILE_NAME, self.fileDir)

    def __load_cookies_from_file(self):
        return FileUtils.load_from_file(self.fileDir + constant.DEFAULT_COOKIE_FILE_NAME)

    def __load_serial_number_from_file(self):
        return FileUtils.load_from_file(self.fileDir + constant.DEFAULT_SERIAL_NUMBER_FILE_NAME)

    def __clear_cookie(self):
        FileUtils.delete_file(self.fileDir + '/' + constant.DEFAULT_COOKIE_FILE_NAME)

    def __clear_serial_numbr(self):
        FileUtils.delete_file(self.fileDir + '/' + constant.DEFAULT_SERIAL_NUMBER_FILE_NAME)
