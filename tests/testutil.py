import json
import os
import tempfile
import uuid
import responses


class TestUtil:

    @staticmethod
    def path(file):
        return os.path.join(os.path.dirname(__file__), file)

    @staticmethod
    def temp_path():
        return tempfile.gettempdir() + "/" + str(uuid.uuid4())

    @staticmethod
    def mock_auth():
        with open(TestUtil.path('files/responses/facilities'), 'r') as file:
            facilities_data = json.loads(file.read())

        with open(TestUtil.path('files/responses/token'), 'r') as file:
            token_data = json.loads(file.read())

        responses.add(responses.POST, 'https://mock.com/account/authentication/v1/token/new', json=token_data,
                      status=200)

        responses.add(responses.POST, 'https://mock.com/account/authentication/v1/authenticate', status=200)
        responses.add(responses.GET, 'https://mock.com/facilities', json=facilities_data, status=200)

        return facilities_data["body"]["facilitiesList"][0]["serialNumber"]
