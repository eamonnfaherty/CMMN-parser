"""CMMN Parser Exceptions"""


class CMMNError(Exception):
    """Base exception for CMMN parser errors."""

    pass


class CMMNParsingError(CMMNError):
    """Raised when CMMN content cannot be parsed."""

    pass


class CMMNValidationError(CMMNError):
    """Raised when CMMN content fails validation."""

    pass


class CMMNFileError(CMMNError):
    """Raised when there are file-related errors."""

    pass
