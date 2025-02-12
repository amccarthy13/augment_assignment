class FundNotFoundException(Exception):

    status_code = 404
    description = "Fund does not exist."

    def __init__(self, message=None, status_code=None, **kwargs):
        super().__init__(message or self.description)
        self.status_code = status_code or self.status_code
        self.metadata = dict(**kwargs)