
class AmountNotPositiveException(Exception):

    status_code = 400
    description = "Amount must be greater than 0."

    def __init__(self, message=None, status_code=None, **kwargs):
        super().__init__(message or self.description)
        self.status_code = status_code or self.status_code
        self.metadata = dict(**kwargs)