from requests import Response


class ApiError(Exception):
    """
    This exception is thrown when a communication error occurs with the vaillant API

    Attributes:
        message: A message describing the error
        response: The response returned by the API

    Args:
        message: A message describing the error
        response: The response returned by the API, if any
    """

    def __init__(self, message: str, response: Response, payload=None):
        self.message = message
        self.response = response
        self.payload = payload
