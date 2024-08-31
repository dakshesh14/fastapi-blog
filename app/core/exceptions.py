class APIError(Exception):
    """
    Base exception class
    """

    def __init__(
        self, message: str = "Unknown error occurred.", name: str = "Error"
    ) -> None:
        self.message = message
        self.name = name
        super().__init__(self.message, self.name)


class EntityNotFound(APIError):
    pass


class EntityAlreadyExist(APIError):
    pass


class BadRequest(APIError):
    pass


class AuthenticationFailed(APIError):
    pass


class AuthorizationFailed(APIError):
    pass
