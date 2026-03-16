class AppError(Exception):
    """Base application error with an error code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
