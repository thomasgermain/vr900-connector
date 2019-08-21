"""Low level connector module."""
import logging
from typing import Optional, Dict, Any

import attr
import requests
from requests import Response

from . import ApiError, urls, defaults
from ..util import fileutils

_LOGGER = logging.getLogger('Connector')

_JSON_CONTENT_TYPE_HEADER = {'content-type': 'application/json'}


@attr.s
class ApiConnector:
    """This is the low level smart.vaillant.com API connector.

    This is returning the raw JSON from responses or an *ApiError* if something
    goes wrong (basically, when response error code is 4xx or 5xx).

    On the first call, the connector will login automatically (if *login* was
    not called previously).

    On following calls, if login doesn't succeed the first time, it will try to
    clear cookies and login a second time (only if response error code is 401)
    before raising an *ApiError*`. This also means the connector is able to
    reconnect automatically when cookies are outdated.

    Please use *urls* module in order to generate URL to be passed to the
    connector.
    """

    _user = attr.ib(type=str)
    _password = attr.ib(type=str, repr=False)
    _smartphone_id = attr.ib(type=str, default=defaults.SMARTPHONE_ID)
    _file_path = attr.ib(type=str, default=defaults.FILES_PATH)
    _serial_number = attr.ib(type=Optional[str], default=None, init=False)
    _session = attr.ib(type=requests.Session, default=None, init=False)

    def __attrs_post_init__(self) -> None:
        self._serial_number = self._load_serial_number_from_file()
        self._session = self._create_or_load_session()

    def login(self, force_login: bool = False) -> bool:
        """Log in to API. Returns True/False.

        By default, the *connector* will try to use cookie located under
        *file_path*. If you set *force_login* to *True*, then the connector
        will clear cookies and start a new authentication.
        """
        try:
            return self._authentication(force_login)
        except ApiError:
            return False

    def logout(self) -> None:
        """Get logged out of the API.

        It first sends a *logout* request to the API (it means cookies are
        invalidated).

        Second, cookies will be cleared.

        The connector will have to request a new token and ask for cookies if
        a new request is done.
        """
        response = None
        try:
            response = self._session.request('POST', urls.logout())
        except Exception as exc:
            raise ApiError("Error during logout", response) from exc
        finally:
            self._clear_session()

    def query(self, url: str, method: str = 'GET',
              payload: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """Call the vaillant API url with the chosen method, please use *urls*
        module in order to generate the URL to be passed to the connector.
        """

        return self._safe_call(method, url, payload)

    def get(self, url: str) -> Optional[Any]:
        """Create a GET call to a vaillant API, please use *urls*
        module in order to generate the URL to be passed to the connector.
        """
        return self.query(url)

    def put(self, url: str, payload: Optional[Dict[str, Any]] = None) \
            -> Optional[Any]:
        """Create a PUT call to a vaillant API, please use *urls*
        module in order to generate the URL to be passed to the connector.
        """
        return self.query(url, 'PUT', payload)

    def post(self, url: str, payload: Optional[Dict[str, Any]] = None) \
            -> Optional[Any]:
        """Create a POST call to a vaillant API, please use *urls*
        module in order to generate the URL to be passed to the connector.
        """
        return self.query(url, 'POST', payload)

    def delete(self, url: str) -> Optional[Any]:
        """Create a DELETE call to a vaillant API, please use *urls*
        module in order to generate the URL to be passed to the connector.
        """
        return self.query(url, 'DELETE')

    def _safe_call(self, method: str, url: str,
                   payload: Optional[Dict[str, Any]] = None,
                   re_login: bool = False) -> Optional[Any]:
        """Call the API using selected *method*, *url* and *payload*.

        This is *safe* in a sense the connector ensure you are logged in.

        The replacement of *serial_number* placeholder in *url* is done here.
        """
        response: Optional[Response] = None
        safe_url: Optional[str] = None

        try:
            self._authentication(re_login)

            safe_url = url.format(serial_number=self._serial_number)
            header = None if payload is None else _JSON_CONTENT_TYPE_HEADER
            response = self._session.request(method,
                                             safe_url,
                                             json=payload,
                                             headers=header)

            if response is not None:
                if response.status_code > 399:
                    if not re_login and response.status_code == 401:
                        _LOGGER.debug('Call to %s failed with HTTP 401, '
                                      'will try to re-login', safe_url)
                        return self._safe_call(method, url, payload, True)

                    raise ApiError(
                        'Received error from server url: {} and method {}'
                        .format(safe_url, method),
                        response,
                        payload)

                return self._return_json(response)

            raise ApiError('Cannot {} url: {}'.format(method, safe_url),
                           response,
                           payload)
        except ApiError:
            raise
        except Exception as exc:
            raise ApiError(
                'Cannot {} url: {}'
                .format(method, safe_url if safe_url else url),
                response,
                payload) from exc

    # pylint: disable=no-self-use
    def _return_json(self, response: Response) -> Optional[Any]:
        if response.text:
            return response.json()
        return None

    def _authentication(self, force_login: bool = False) -> bool:
        try:
            if force_login:
                self._clear_session()

            if not self._session.cookies:
                self._session = self._create_or_load_session()
                self._serial_number = self._load_serial_number_from_file()

                if not self._session.cookies:
                    _LOGGER.info('No previous session found, will try to log '
                                 'in with username: %s and smartphoneId: %s',
                                 self._user, self._smartphone_id)

                    auth_token = self._request_token()
                    self._get_cookies(auth_token)

            if not self._serial_number:
                self._get_serial_number()

            return True
        except ApiError:
            raise
        except Exception as exc:
            raise ApiError('Error during login', None) from exc

    def _request_token(self) -> str:
        params = {
            "smartphoneId": self._smartphone_id,
            "username": self._user,
            "password": self._password
        }

        try:
            response = self._session.post(urls.new_token(), json=params,
                                          headers=_JSON_CONTENT_TYPE_HEADER)
            if response.status_code == 200:
                _LOGGER.debug('Token generation successful')
                return str(response.json()['body']['authToken'])

            params['password'] = '*****'
            raise ApiError('Authentication failed', response, params)

        except ApiError:
            raise
        except Exception as exc:
            raise ApiError('Error during authentication', None) from exc

    def _get_cookies(self, auth_token: str) -> None:
        params = {
            "smartphoneId": self._smartphone_id,
            "username": self._user,
            "authToken": auth_token
        }

        try:
            response = self._session.post(urls.authenticate(), json=params,
                                          headers=_JSON_CONTENT_TYPE_HEADER)

            if response.status_code == 200:
                self._session.cookies = response.cookies
                _LOGGER.debug('Cookie successfully retrieved %s',
                              self._session.cookies)
                self._save_cookies_to_file()
            else:
                params["authToken"] = "******"
                raise ApiError('Cannot get cookies', response, params)
        except ApiError:
            raise
        except Exception as exc:
            raise ApiError('Error while getting cookies', None) from exc

    def _get_serial_number(self) -> None:
        try:
            response = self._session.get(urls.facilities_list())

            if response.status_code == 200:
                _LOGGER.debug('Serial number successfully retrieved')
                self._serial_number = \
                    response.json()['body']['facilitiesList'][0][
                        'serialNumber']
                self._save_serial_number_to_file()
            else:
                raise ApiError('Cannot get serial number', response)
        except ApiError:
            raise
        except Exception as exc:
            raise ApiError('Cannot get serial number', None) from exc

    def _create_or_load_session(self) -> requests.Session:
        session = requests.Session()
        cookies = self._load_cookies_from_file()
        _LOGGER.debug('Found cookies %s', cookies)
        if cookies is not None:
            session.cookies = cookies
        return session

    def _clear_session(self) -> None:
        self._clear_cookie()
        self._clear_serial_number()
        self._session.close()
        self._session = requests.session()
        fileutils.delete_dir(self._file_path)

    def _save_cookies_to_file(self) -> None:
        fileutils.save_to_file(self._session.cookies, self._file_path,
                               defaults.COOKIE_FILE_NAME)

    def _save_serial_number_to_file(self) -> None:
        fileutils.save_to_file(self._serial_number, self._file_path,
                               defaults.SERIAL_NUMBER_FILE_NAME)

    def _load_cookies_from_file(self) -> Any:
        return fileutils.load_from_file(self._file_path,
                                        defaults.COOKIE_FILE_NAME)

    def _load_serial_number_from_file(self) -> Optional[str]:
        result = fileutils.load_from_file(self._file_path,
                                          defaults.SERIAL_NUMBER_FILE_NAME)

        if result:
            return str(result)
        return None

    def _clear_cookie(self) -> None:
        fileutils.delete_file(self._file_path, defaults.COOKIE_FILE_NAME)

    def _clear_serial_number(self) -> None:
        fileutils.delete_file(self._file_path,
                              defaults.SERIAL_NUMBER_FILE_NAME)
        self._serial_number = None
