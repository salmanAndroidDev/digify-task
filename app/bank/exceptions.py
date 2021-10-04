from django.db import IntegrityError


class AccountAlreadyExistError(IntegrityError):
    """
        This exception is raised when there is more than 1 account in the bank
        for each user
    """
    def __init__(self, message='There is already an account with this user'):
        super().__init__(message)
