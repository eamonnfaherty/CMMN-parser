"""Tests for CMMN parser functionality."""

import os
import tempfile
from unittest.mock import mock_open, patch

import pytest

from cmmn_parser.exceptions import CMMNParsingError, CMMNValidationError
from cmmn_parser.models import CMMNDefinitions
from cmmn_parser.parser import CMMNParser


class TestCMMNParser:
    """Test CMMN parser functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = CMMNParser()

        self.sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/CMMN/20151109/MODEL"
             id="def1" name="Test Definitions">
    <case id="case1" name="Test Case">
        <casePlanModel id="cpm1" name="Case Plan Model" autoComplete="false">
            <task id="task1" name="Test Task" isBlocking="true"/>
        </casePlanModel>
    </case>
</definitions>"""

        self.sample_json = """{
    "id": "def1",
    "name": "Test Definitions",
    "cases": [{
        "id": "case1",
        "name": "Test Case",
        "casePlanModel": {
            "id": "cpm1",
            "name": "Case Plan Model",
            "autoComplete": false,
            "tasks": [{
                "id": "task1",
                "name": "Test Task",
                "isBlocking": true,
                "type": "task"
            }]
        }
    }]
}"""

    def test_parser_initialization(self):
        """Test parser initialization."""
        parser = CMMNParser()
        assert parser.xml_parser is not None
        assert parser.json_parser is not None
        assert parser.validator is not None

    def test_parse_empty_string_raises_error(self):
        """Test that parsing empty string raises error."""
        with pytest.raises(CMMNParsingError, match="Content cannot be empty"):
            self.parser.parse_string("")

        with pytest.raises(CMMNParsingError, match="Content cannot be empty"):
            self.parser.parse_string("   ")

    def test_parse_xml_string_auto_detection(self):
        """Test parsing XML string with auto format detection."""
        result = self.parser.parse_string(self.sample_xml, "auto")
        assert isinstance(result, CMMNDefinitions)
        assert result.id == "def1"
        assert result.name == "Test Definitions"
        assert len(result.cases) == 1
        assert result.cases[0].id == "case1"

    def test_parse_json_string_auto_detection(self):
        """Test parsing JSON string with auto format detection."""
        result = self.parser.parse_string(self.sample_json, "auto")
        assert isinstance(result, CMMNDefinitions)
        assert result.id == "def1"
        assert result.name == "Test Definitions"
        assert len(result.cases) == 1
        assert result.cases[0].id == "case1"

    def test_parse_xml_string_explicit(self):
        """Test parsing XML string with explicit format."""
        result = self.parser.parse_xml_string(self.sample_xml)
        assert isinstance(result, CMMNDefinitions)
        assert result.id == "def1"

    def test_parse_json_string_explicit(self):
        """Test parsing JSON string with explicit format."""
        result = self.parser.parse_json_string(self.sample_json)
        assert isinstance(result, CMMNDefinitions)
        assert result.id == "def1"

    def test_parse_invalid_xml_raises_error(self):
        """Test that parsing invalid XML raises error."""
        invalid_xml = "<invalid><unclosed>"
        with pytest.raises(CMMNParsingError):
            self.parser.parse_xml_string(invalid_xml)

    def test_parse_invalid_json_raises_error(self):
        """Test that parsing invalid JSON raises error."""
        invalid_json = '{"invalid": json}'
        with pytest.raises(CMMNParsingError, match="Invalid JSON"):
            self.parser.parse_json_string(invalid_json)

    def test_detect_format_xml(self):
        """Test format detection for XML."""
        xml_content = '<?xml version="1.0"?><root/>'
        result = self.parser._detect_format(xml_content, "auto")
        assert result == "xml"

        xml_content2 = "<root/>"
        result2 = self.parser._detect_format(xml_content2, "auto")
        assert result2 == "xml"

    def test_detect_format_json(self):
        """Test format detection for JSON."""
        json_content = '{"key": "value"}'
        result = self.parser._detect_format(json_content, "auto")
        assert result == "json"

        json_array = '[{"key": "value"}]'
        result2 = self.parser._detect_format(json_array, "auto")
        assert result2 == "json"

    def test_detect_format_explicit(self):
        """Test explicit format specification."""
        content = "some content"
        result_xml = self.parser._detect_format(content, "xml")
        assert result_xml == "xml"

        result_json = self.parser._detect_format(content, "json")
        assert result_json == "json"

    def test_detect_format_unknown_raises_error(self):
        """Test that unknown format raises error."""
        content = "unknown content"
        with pytest.raises(CMMNParsingError, match="Unable to auto-detect format"):
            self.parser._detect_format(content, "auto")

        with pytest.raises(CMMNParsingError, match="Unknown format type"):
            self.parser._detect_format(content, "unknown")

    def test_detect_format_from_path(self):
        """Test format detection from file path."""
        assert self.parser._detect_format_from_path("file.xml") == "xml"
        assert self.parser._detect_format_from_path("file.cmmn") == "xml"
        assert self.parser._detect_format_from_path("file.json") == "json"
        assert self.parser._detect_format_from_path("file.txt") == "auto"

    def test_parse_file_not_found(self):
        """Test parsing non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            self.parser.parse_file("nonexistent_file.xml")

    def test_parse_xml_file(self):
        """Test parsing XML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(self.sample_xml)
            temp_path = f.name

        try:
            result = self.parser.parse_xml_file(temp_path)
            assert isinstance(result, CMMNDefinitions)
            assert result.id == "def1"
        finally:
            os.unlink(temp_path)

    def test_parse_json_file(self):
        """Test parsing JSON file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write(self.sample_json)
            temp_path = f.name

        try:
            result = self.parser.parse_json_file(temp_path)
            assert isinstance(result, CMMNDefinitions)
            assert result.id == "def1"
        finally:
            os.unlink(temp_path)

    def test_parse_file_with_auto_format(self):
        """Test parsing file with auto format detection."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(self.sample_xml)
            temp_path = f.name

        try:
            result = self.parser.parse_file(temp_path, "auto")
            assert isinstance(result, CMMNDefinitions)
            assert result.id == "def1"
        finally:
            os.unlink(temp_path)

    @patch("builtins.open", side_effect=IOError("Read error"))
    def test_parse_file_read_error(self, mock_file):
        """Test file read error handling."""
        with patch("os.path.exists", return_value=True):
            with pytest.raises(Exception):
                self.parser.parse_file("test.xml")

    def test_validate_xml_string(self):
        """Test XML string validation."""
        with patch.object(self.parser.validator, "validate_xml", return_value=True):
            result = self.parser.validate_xml_string(self.sample_xml)
            assert result is True

    def test_validate_json_string(self):
        """Test JSON string validation."""
        with patch.object(self.parser.validator, "validate_json", return_value=True):
            result = self.parser.validate_json_string(self.sample_json)
            assert result is True

    def test_validate_json_string_invalid_json(self):
        """Test JSON validation with invalid JSON."""
        invalid_json = '{"invalid": json}'
        with pytest.raises(CMMNValidationError, match="Invalid JSON"):
            self.parser.validate_json_string(invalid_json)

    def test_validate_xml_file(self):
        """Test XML file validation."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(self.sample_xml)
            temp_path = f.name

        try:
            with patch.object(self.parser.validator, "validate_xml", return_value=True):
                result = self.parser.validate_xml_file(temp_path)
                assert result is True
        finally:
            os.unlink(temp_path)

    def test_validate_json_file(self):
        """Test JSON file validation."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write(self.sample_json)
            temp_path = f.name

        try:
            with patch.object(
                self.parser.validator, "validate_json", return_value=True
            ):
                result = self.parser.validate_json_file(temp_path)
                assert result is True
        finally:
            os.unlink(temp_path)

    def test_validate_file_not_found(self):
        """Test validation of non-existent file."""
        with pytest.raises(FileNotFoundError):
            self.parser.validate_xml_file("nonexistent.xml")

        with pytest.raises(FileNotFoundError):
            self.parser.validate_json_file("nonexistent.json")
