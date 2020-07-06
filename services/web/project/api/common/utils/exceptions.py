from pydantic import ValidationError


class APIException(Exception):
    """
    Base API Exception
    """

    def __init__(self, message, status_code, payload, name):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload
        self.name = name

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['code'] = self.status_code
        rv['name'] = self.name
        rv['message'] = self.message
        return rv


class InvalidPayloadException(APIException):
    """
    400 Invalid Payload Exception
    """

    def __init__(self, message: str = 'Invalid Payload', payload=None, name='Invalid Payload'):
        super().__init__(message=message, status_code=400, payload=payload, name=name)


class ValidationException(InvalidPayloadException):
    """
    400 Invalid Payload Exception with Validation Errors
    """

    def __init__(self, e: ValidationError, message: str = 'Validation Error'):
        payload = dict({'message': 'validation errors',
                   'errors': [{'field': error['loc'][0], 'message': error['msg']}
                              for error in e.errors()]})
        super().__init__(message=message, payload=payload)


class BadRequestException(APIException):
    """
    400 Bad Request Exception
    """

    def __init__(self, message: str = 'Bad Request', payload=None, name='Bad Request'):
        super().__init__(message=message, status_code=400, payload=payload, name=name)


class UnauthorizedException(APIException):
    """
    401 Unauthorized Exception
    """

    def __init__(self, message: str = 'Not Authorized to perform this action', payload=None, name='Unauthorized'):
        super().__init__(message=message, status_code=401, payload=payload, name=name)


class ForbiddenException(APIException):
    """
    403 Forbidden Exception
    """

    def __init__(self, message: str = 'Forbidden', payload=None, name='Forbidden'):
        super().__init__(message=message, status_code=403, payload=payload, name=name)


class NotFoundException(APIException):
    """
    404 Not Found Exception
    """

    def __init__(self, message: str = 'The requested URL was not found on the server.',
                 payload=None, name: str = 'Not Found'):
        super().__init__(message=message, status_code=404, payload=payload, name=name)


class ServerErrorException(APIException):
    """
    500 Internal Server Error Exception
    """

    def __init__(self, message: str = 'Something went wrong', payload=None, name='Internal Server Error'):
        super().__init__(message=message, status_code=500, payload=payload, name=name)


class NotImplementedException(APIException):
    """
    501 Not Implemented Exception
    """

    def __init__(self, message: str = 'The method is not implemented for the requested URL.', payload=None,
                 name='Not Implemented'):
        super().__init__(message=message, status_code=501, payload=payload, name=name)


class MethodNotAllowedException(APIException):
    """
    405 Method Not Allowed
    """

    def __init__(self, message: str = 'The method is not allowed for the requested URL.', payload=None,
                 name='Method Not Allowed'):
        super().__init__(message=message, status_code=405, payload=payload, name=name)
