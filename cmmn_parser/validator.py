"""CMMN Validator

Validates CMMN XML against XSD schema and JSON against JSON schema.
"""

from pathlib import Path
from typing import Any, Dict, Optional

try:
    from lxml import etree
except ImportError:
    etree = None

try:
    import jsonschema
    from jsonschema import SchemaError as JSONSchemaError
    from jsonschema import ValidationError as JSONValidationError
except ImportError:
    jsonschema = None
    JSONValidationError = None
    JSONSchemaError = None

from .exceptions import CMMNValidationError


class CMMNValidator:
    """Validator for CMMN XML and JSON formats."""

    def __init__(self) -> None:
        """Initialize the validator."""
        self.schema_dir = Path(__file__).parent.parent / "references"
        self._xml_schema = None
        self._json_schema: Optional[Dict[str, Any]] = None

    def validate_xml(self, xml_content: str) -> bool:
        """Validate XML content against CMMN XSD schema.

        Args:
            xml_content: The XML content as a string

        Returns:
            bool: True if valid

        Raises:
            CMMNValidationError: If validation fails
        """
        if etree is None:
            raise CMMNValidationError("lxml is required for XML validation")

        if self._xml_schema is None:
            self._load_xml_schema()

        try:
            doc = etree.fromstring(xml_content.encode("utf-8"))
            assert self._xml_schema is not None
            self._xml_schema.assertValid(doc)
            return True
        except etree.DocumentInvalid as e:
            raise CMMNValidationError(f"XML validation failed: {e}")
        except etree.XMLSyntaxError as e:
            raise CMMNValidationError(f"XML syntax error: {e}")

    def validate_json(self, json_data: Dict[str, Any]) -> bool:
        """Validate JSON data against CMMN JSON schema.

        Args:
            json_data: The JSON data as a dictionary

        Returns:
            bool: True if valid

        Raises:
            CMMNValidationError: If validation fails
        """
        if jsonschema is None:
            raise CMMNValidationError("jsonschema is required for JSON validation")

        if self._json_schema is None:
            self._load_json_schema()

        try:
            jsonschema.validate(json_data, self._json_schema)
            return True
        except JSONValidationError as e:
            raise CMMNValidationError(f"JSON validation failed: {e.message}")
        except JSONSchemaError as e:
            raise CMMNValidationError(f"JSON schema error: {e.message}")

    def _load_xml_schema(self) -> None:
        """Load the XML schema for validation."""
        if etree is None:
            raise CMMNValidationError("lxml is required for XML schema loading")

        schema_file = self.schema_dir / "CMMN11.xsd"

        if not schema_file.exists():
            raise CMMNValidationError(f"XML schema file not found: {schema_file}")

        try:
            with open(schema_file, "r", encoding="utf-8") as f:
                schema_doc = etree.parse(f)
            self._xml_schema = etree.XMLSchema(schema_doc)
        except Exception as e:
            raise CMMNValidationError(f"Failed to load XML schema: {e}")

    def _load_json_schema(self) -> None:
        """Load the JSON schema for validation."""
        self._json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "title": "CMMN Definitions Schema",
            "description": "Schema for CMMN definitions in JSON format",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "targetNamespace": {"type": "string"},
                "expressionLanguage": {"type": "string"},
                "exporter": {"type": "string"},
                "exporterVersion": {"type": "string"},
                "author": {"type": "string"},
                "creationDate": {"type": "string"},
                "imports": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "namespace": {"type": "string"},
                            "location": {"type": "string"},
                            "importType": {"type": "string"},
                        },
                    },
                },
                "caseFileItemDefinitions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "structureRef": {"type": "string"},
                            "definitiveProperty": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                    },
                },
                "cases": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "casePlanModel": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "name": {"type": "string"},
                                    "autoComplete": {"type": "boolean"},
                                    "planItems": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "string"},
                                                "name": {"type": "string"},
                                                "definitionRef": {"type": "string"},
                                                "entryCriteria": {
                                                    "type": "array",
                                                    "items": {"type": "string"},
                                                },
                                                "exitCriteria": {
                                                    "type": "array",
                                                    "items": {"type": "string"},
                                                },
                                            },
                                        },
                                    },
                                    "sentries": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "string"},
                                                "name": {"type": "string"},
                                                "onPart": {
                                                    "type": "array",
                                                    "items": {"type": "string"},
                                                },
                                                "ifPart": {"type": "string"},
                                            },
                                        },
                                    },
                                    "stages": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "string"},
                                                "name": {"type": "string"},
                                                "autoComplete": {"type": "boolean"},
                                                "planItems": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "id": {"type": "string"},
                                                            "name": {"type": "string"},
                                                            "definitionRef": {
                                                                "type": "string"
                                                            },
                                                            "entryCriteria": {
                                                                "type": "array",
                                                                "items": {
                                                                    "type": "string"
                                                                },
                                                            },
                                                            "exitCriteria": {
                                                                "type": "array",
                                                                "items": {
                                                                    "type": "string"
                                                                },
                                                            },
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                    "tasks": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "string"},
                                                "name": {"type": "string"},
                                                "type": {"type": "string"},
                                                "isBlocking": {"type": "boolean"},
                                                "taskType": {"type": "string"},
                                                "performer": {"type": "string"},
                                                "formKey": {"type": "string"},
                                                "processRef": {"type": "string"},
                                                "caseRef": {"type": "string"},
                                                "decisionRef": {"type": "string"},
                                            },
                                        },
                                    },
                                    "milestones": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "string"},
                                                "name": {"type": "string"},
                                                "description": {"type": "string"},
                                            },
                                        },
                                    },
                                },
                            },
                            "caseFileModel": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "name": {"type": "string"},
                                    "caseFileItems": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                },
                            },
                        },
                    },
                },
                "processes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "isExecutable": {"type": "boolean"},
                            "implementationType": {"type": "string"},
                        },
                    },
                },
                "decisions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "decisionLogic": {"type": "string"},
                        },
                    },
                },
                "extensionElements": {"type": "object", "additionalProperties": True},
            },
            "additionalProperties": False,
        }
