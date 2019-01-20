class ApiError(Exception):
    def __init__(self, message, response):
        self.message = message
        self.response = response
