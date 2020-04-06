from jsonrpcbase import JSONRPCError


class ServiceError(JSONRPCError):
    def __init__(self, code=None, message=None, data=None):
        super(ServiceError, self).__init__(message)
        self.code = code
        self.data = data
