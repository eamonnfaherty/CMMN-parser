"""CMMN Parser Library

A parsing library for CMMN (Case Management Model and Notation) with XML and JSON support.
"""

from .exceptions import CMMNParsingError, CMMNValidationError
from .models import CMMNDefinitions
from .parser import CMMNParser

__version__ = "0.1.0"
__all__ = ["CMMNParser", "CMMNDefinitions", "CMMNParsingError", "CMMNValidationError"]


def parse_cmmn_string(content: str, format_type: str = "auto") -> CMMNDefinitions:
    """Convenience function to parse CMMN content from a string.

    Args:
        content: The CMMN content as a string
        format_type: The format type ('xml', 'json', or 'auto')

    Returns:
        CMMNDefinitions: Parsed CMMN definitions

    Raises:
        CMMNParsingError: If parsing fails
        CMMNValidationError: If validation fails
    """
    parser = CMMNParser()
    return parser.parse_string(content, format_type)


def parse_cmmn_file(file_path: str, format_type: str = "auto") -> CMMNDefinitions:
    """Convenience function to parse CMMN content from a file.

    Args:
        file_path: Path to the CMMN file
        format_type: The format type ('xml', 'json', or 'auto')

    Returns:
        CMMNDefinitions: Parsed CMMN definitions

    Raises:
        CMMNParsingError: If parsing fails
        CMMNValidationError: If validation fails
        FileNotFoundError: If file doesn't exist
    """
    parser = CMMNParser()
    return parser.parse_file(file_path, format_type)
