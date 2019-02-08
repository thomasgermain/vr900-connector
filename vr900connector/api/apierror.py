from requests import Response


class ApiError(Exception):
    message: str = None
    response: Response = None

    def __init__(self, message, response):
        self.message = message
        self.response = response
