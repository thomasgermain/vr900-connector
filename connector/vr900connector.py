from connector import constant
import requests
import pickle
import os


class Vr900Connector:

    def __init__(self, user, password, smartphone_id=None, base_url=None, cookie_dir=None):
        self.user = user
        self.password = password
        self.smartphoneId = smartphone_id if smartphone_id is not None else constant.DEFAULT_SMARTPHONE_ID
        self.baseUrl = base_url if base_url is not None else constant.DEFAULT_BASE_URL
        self.cookieDir = cookie_dir if cookie_dir is not None else constant.DEFAULT_COOKIE_LOCATION
        self.headers = {'content-type': 'application/json'}
        self.__session = None
        self.__serialNumber = None

    def login(self):
        self.__session = requests.session()
        self.__load_cookies_from_file()

        if self.__session is None:

            try:
                authtoken = self.__request_token()
                if authtoken is not None:
                    self.__get_cookies(authtoken)
            finally:
                self.__session.close()

    def __request_token(self):
        params = {
            'smartphoneId': self.smartphoneId,
            'username': self.user,
            'password': self.password
        }

        response = self.__session.post(self.baseUrl + constant.REQUEST_NEW_TOKEN_URL, json=params, headers=self.headers)
        if response.status_code == 200:
            return response.json()['body']['authToken']
        else:
            return None

    def __get_cookies(self, authtoken):
        params = {
            'smartphoneId': self.smartphoneId,
            'username': self.user,
            'authToken': authtoken
        }
        response = self.__session.post(self.baseUrl + constant.AUTHENTICATE_URL, json=params, headers=self.headers)

        if response.status_code == 200:
            self.__save_cookies_to_file()

    def __save_cookies_to_file(self):
        os.makedirs(self.cookieDir, exist_ok=True)
        with open(self.cookieDir + '/.vaillant.cookies', 'wb+') as f:
            pickle.dump(self.__session, f)

    def __load_cookies_from_file(self):
        try:
            with open(self.cookieDir + '/.vaillant.cookies', 'rb') as f:
                self.__session.cookies.update(pickle.load(f))
        except:
            self.__session.cookies = None
