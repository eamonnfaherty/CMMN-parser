"""Tests for CMMN exceptions."""

import pytest

from cmmn_parser.exceptions import (
    CMMNError,
    CMMNFileError,
    CMMNParsingError,
    CMMNValidationError,
)


class TestCMMNExceptions:
    """Test CMMN exception classes."""

    def test_cmmn_error_base_class(self):
        """Test base CMMN error class."""
        error = CMMNError("Base error")
        assert str(error) == "Base error"
        assert isinstance(error, Exception)

    def test_cmmn_parsing_error(self):
        """Test CMMN parsing error."""
        error = CMMNParsingError("Parsing failed")
        assert str(error) == "Parsing failed"
        assert isinstance(error, CMMNError)
        assert isinstance(error, Exception)

    def test_cmmn_validation_error(self):
        """Test CMMN validation error."""
        error = CMMNValidationError("Validation failed")
        assert str(error) == "Validation failed"
        assert isinstance(error, CMMNError)
        assert isinstance(error, Exception)

    def test_cmmn_file_error(self):
        """Test CMMN file error."""
        error = CMMNFileError("File error")
        assert str(error) == "File error"
        assert isinstance(error, CMMNError)
        assert isinstance(error, Exception)

    def test_exception_inheritance(self):
        """Test exception inheritance hierarchy."""
        # Test that all exceptions inherit properly
        assert issubclass(CMMNParsingError, CMMNError)
        assert issubclass(CMMNValidationError, CMMNError)
        assert issubclass(CMMNFileError, CMMNError)
        assert issubclass(CMMNError, Exception)

    def test_exception_raising(self):
        """Test that exceptions can be raised and caught."""
        with pytest.raises(CMMNParsingError):
            raise CMMNParsingError("Test parsing error")

        with pytest.raises(CMMNValidationError):
            raise CMMNValidationError("Test validation error")

        with pytest.raises(CMMNFileError):
            raise CMMNFileError("Test file error")

        with pytest.raises(CMMNError):
            raise CMMNError("Test base error")

    def test_exception_catching_base_class(self):
        """Test that derived exceptions can be caught by base class."""
        try:
            raise CMMNParsingError("Parsing error")
        except CMMNError as e:
            assert str(e) == "Parsing error"
            assert isinstance(e, CMMNParsingError)

        try:
            raise CMMNValidationError("Validation error")
        except CMMNError as e:
            assert str(e) == "Validation error"
            assert isinstance(e, CMMNValidationError)

        try:
            raise CMMNFileError("File error")
        except CMMNError as e:
            assert str(e) == "File error"
            assert isinstance(e, CMMNFileError)
