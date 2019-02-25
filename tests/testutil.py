import json
import os
import tempfile
import uuid
import responses

from vr900connector.api import urls


class TestUtil:

    @staticmethod
    def path(file):
        return os.path.join(os.path.dirname(__file__), file)

    @staticmethod
    def temp_path():
        path = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
        os.mkdir(path)
        return path

    @staticmethod
    def mock_auth_success():
        with open(TestUtil.path('files/responses/facilities'), 'r') as file:
            facilities_data = json.loads(file.read())

        with open(TestUtil.path('files/responses/token'), 'r') as file:
            token_data = json.loads(file.read())

        responses.add(responses.POST, urls.new_token(), json=token_data, status=200)
        responses.add(responses.POST, urls.authenticate(), status=200,
                      headers={"Set-Cookie": "test=value; path=/; HttpOnly; Secure"})
        responses.add(responses.GET, urls.facilities_list(), json=facilities_data, status=200)

        return facilities_data["body"]["facilitiesList"][0]["serialNumber"]

    @classmethod
    def mock_logout(cls):
        responses.add(responses.POST, urls.logout(), status=200, headers={"Set-Cookies": ""})
