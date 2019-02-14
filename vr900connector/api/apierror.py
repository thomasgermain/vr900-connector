class ApiError(Exception):
    message = None
    response = None

    def __init__(self, message, response):
        self.message = message
        self.response = response
