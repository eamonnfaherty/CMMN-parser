"""CMMN Parser

Main parsing functionality for CMMN XML and JSON formats.
"""

import json
import os
from pathlib import Path

from .exceptions import CMMNFileError, CMMNParsingError, CMMNValidationError
from .json_parser import JSONParser
from .models import CMMNDefinitions
from .validator import CMMNValidator
from .xml_parser import XMLParser


class CMMNParser:
    """Main CMMN parser supporting both XML and JSON formats."""

    def __init__(self) -> None:
        """Initialize the CMMN parser."""
        self.xml_parser = XMLParser()
        self.json_parser = JSONParser()
        self.validator = CMMNValidator()

    def parse_string(self, content: str, format_type: str = "auto") -> CMMNDefinitions:
        """Parse CMMN content from a string.

        Args:
            content: The CMMN content as a string
            format_type: The format type ('xml', 'json', or 'auto')

        Returns:
            CMMNDefinitions: Parsed CMMN definitions

        Raises:
            CMMNParsingError: If parsing fails
            CMMNValidationError: If validation fails
        """
        if not content or not content.strip():
            raise CMMNParsingError("Content cannot be empty")

        detected_format = self._detect_format(content, format_type)

        if detected_format == "xml":
            return self.parse_xml_string(content)
        elif detected_format == "json":
            return self.parse_json_string(content)
        else:
            raise CMMNParsingError(f"Unable to determine format: {format_type}")

    def parse_file(self, file_path: str, format_type: str = "auto") -> CMMNDefinitions:
        """Parse CMMN content from a file.

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
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            raise CMMNFileError(f"Error reading file {file_path}: {e}")

        if format_type == "auto":
            format_type = self._detect_format_from_path(file_path)

        return self.parse_string(content, format_type)

    def parse_xml_string(self, xml_content: str) -> CMMNDefinitions:
        """Parse CMMN content from an XML string.

        Args:
            xml_content: The XML content as a string

        Returns:
            CMMNDefinitions: Parsed CMMN definitions

        Raises:
            CMMNParsingError: If XML parsing fails
            CMMNValidationError: If XML validation fails
        """
        try:
            return self.xml_parser.parse(xml_content)
        except Exception as e:
            raise CMMNParsingError(f"Failed to parse XML: {e}")

    def parse_xml_file(self, file_path: str) -> CMMNDefinitions:
        """Parse CMMN content from an XML file.

        Args:
            file_path: Path to the XML file

        Returns:
            CMMNDefinitions: Parsed CMMN definitions

        Raises:
            CMMNParsingError: If parsing fails
            FileNotFoundError: If file doesn't exist
        """
        return self.parse_file(file_path, "xml")

    def parse_json_string(self, json_content: str) -> CMMNDefinitions:
        """Parse CMMN content from a JSON string.

        Args:
            json_content: The JSON content as a string

        Returns:
            CMMNDefinitions: Parsed CMMN definitions

        Raises:
            CMMNParsingError: If JSON parsing fails
            CMMNValidationError: If JSON validation fails
        """
        try:
            data = json.loads(json_content)
            return self.json_parser.parse(data)
        except json.JSONDecodeError as e:
            raise CMMNParsingError(f"Invalid JSON: {e}")
        except Exception as e:
            raise CMMNParsingError(f"Failed to parse JSON: {e}")

    def parse_json_file(self, file_path: str) -> CMMNDefinitions:
        """Parse CMMN content from a JSON file.

        Args:
            file_path: Path to the JSON file

        Returns:
            CMMNDefinitions: Parsed CMMN definitions

        Raises:
            CMMNParsingError: If parsing fails
            FileNotFoundError: If file doesn't exist
        """
        return self.parse_file(file_path, "json")

    def validate_xml_string(self, xml_content: str) -> bool:
        """Validate XML CMMN content against the XSD schema.

        Args:
            xml_content: The XML content as a string

        Returns:
            bool: True if valid

        Raises:
            CMMNValidationError: If validation fails
        """
        return self.validator.validate_xml(xml_content)

    def validate_xml_file(self, file_path: str) -> bool:
        """Validate XML CMMN file against the XSD schema.

        Args:
            file_path: Path to the XML file

        Returns:
            bool: True if valid

        Raises:
            CMMNValidationError: If validation fails
            FileNotFoundError: If file doesn't exist
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            raise CMMNFileError(f"Error reading file {file_path}: {e}")

        return self.validate_xml_string(content)

    def validate_json_string(self, json_content: str) -> bool:
        """Validate JSON CMMN content against the JSON schema.

        Args:
            json_content: The JSON content as a string

        Returns:
            bool: True if valid

        Raises:
            CMMNValidationError: If validation fails
        """
        try:
            data = json.loads(json_content)
            return self.validator.validate_json(data)
        except json.JSONDecodeError as e:
            raise CMMNValidationError(f"Invalid JSON: {e}")

    def validate_json_file(self, file_path: str) -> bool:
        """Validate JSON CMMN file against the JSON schema.

        Args:
            file_path: Path to the JSON file

        Returns:
            bool: True if valid

        Raises:
            CMMNValidationError: If validation fails
            FileNotFoundError: If file doesn't exist
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            raise CMMNFileError(f"Error reading file {file_path}: {e}")

        return self.validate_json_string(content)

    def _detect_format(self, content: str, format_type: str) -> str:
        """Detect the format of the content.

        Args:
            content: The content to analyze
            format_type: Explicit format type or 'auto'

        Returns:
            str: Detected format ('xml' or 'json')
        """
        if format_type in ("xml", "json"):
            return format_type

        if format_type != "auto":
            raise CMMNParsingError(f"Unknown format type: {format_type}")

        content = content.strip()

        if content.startswith("<?xml") or content.startswith("<"):
            return "xml"
        elif content.startswith("{") or content.startswith("["):
            return "json"

        raise CMMNParsingError("Unable to auto-detect format")

    def _detect_format_from_path(self, file_path: str) -> str:
        """Detect format from file extension.

        Args:
            file_path: Path to the file

        Returns:
            str: Detected format ('xml' or 'json')
        """
        path = Path(file_path)
        extension = path.suffix.lower()

        if extension in (".xml", ".cmmn"):
            return "xml"
        elif extension == ".json":
            return "json"

        return "auto"
