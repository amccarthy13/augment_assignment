
class SendingAndReceivingUserSameException(Exception):

    status_code = 400
    description = "Sending and receiving user cannot be the same"

    def __init__(self, message=None, status_code=None, **kwargs):
        super().__init__(message or self.description)
        self.status_code = status_code or self.status_code
        self.metadata = dict(**kwargs)

class SendingUserNotProvidedException(Exception):

    status_code = 400
    description = "Sending user must be provided for transfers."

    def __init__(self, message=None, status_code=None, **kwargs):
        super().__init__(message or self.description)
        self.status_code = status_code or self.status_code
        self.metadata = dict(**kwargs)


class UserNotFoundException(Exception):

    status_code = 404
    description = "User does not exist."

    def __init__(self, message=None, status_code=None, **kwargs):
        super().__init__(message or self.description)
        self.status_code = status_code or self.status_code
        self.metadata = dict(**kwargs)