import json
import os
import tempfile
import uuid
import responses

from vr900connector.api import Urls


class TestUtil:

    @classmethod
    def path(cls, file):
        return os.path.join(os.path.dirname(__file__), file)

    @classmethod
    def temp_path(cls, ):
        path = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
        os.mkdir(path)
        return path

    @classmethod
    def mock_full_auth_success(cls, ):
        TestUtil.mock_authentication_success()
        TestUtil.mock_token_success()
        return TestUtil.mock_serial_success()

    @classmethod
    def mock_token_success(cls, ):
        with open(TestUtil.path('files/responses/token'), 'r') as file:
            token_data = json.loads(file.read())

        responses.add(responses.POST, Urls.new_token(), json=token_data, status=200)

    @classmethod
    def mock_authentication_success(cls, ):
        responses.add(responses.POST, Urls.authenticate(), status=200,
                      headers={"Set-Cookie": "test=value; path=/; Secure; HttpOnly"})

    @classmethod
    def mock_serial_success(cls):
        with open(TestUtil.path('files/responses/facilities'), 'r') as file:
            facilities_data = json.loads(file.read())

        responses.add(responses.GET, Urls.facilities_list(), json=facilities_data, status=200)

        return facilities_data["body"]["facilitiesList"][0]["serialNumber"]

    @classmethod
    def mock_logout(cls):
        responses.add(responses.POST, Urls.logout(), status=200, headers={"Set-Cookies": ""})
