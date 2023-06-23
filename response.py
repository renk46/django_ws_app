class Response:
    """Class for response"""

    def __init__(self, response: str, data: dict, result: str):
        self.response = response
        self.data = data
        self.result = result

    def __hash__(self):
        return hash((self.response, self.data, self.result))

    def __eq__(self, other):
        return (self.response, self.data, self.result) == (
            other.response,
            other.data,
            other.result,
        )

    def __ne__(self, other):
        return self != other

    def get_obj(self):
        """Get object"""
        return {"response": self.response, "data": self.data, "result": self.result}


class SuccessResponse(Response):
    """Class for success response"""

    def __init__(self, response: str, data: dict):
        super(SuccessResponse, self).__init__(response, data, "success")


class FailedResponse(Response):
    """Class for failed response"""

    def __init__(self, response: str, data: dict):
        super(FailedResponse, self).__init__(response, data, "failed")
