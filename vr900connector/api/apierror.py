class ApiError(Exception):
    """
    This exception is thrown when a communication error occurs with the vaillant API

    Args:
        message: A message describing the error
        response: The response returned by the API
    """

    def __init__(self, message, response):
        self.message = message
        self.response = response
