"""Tests for JSON validation functionality."""

import json
from pathlib import Path

import pytest
from cmmn_parser.validation import load_cmmn_schema

from cmmn_parser import (
    CMMNParseError,
    get_schema_info,
    get_validation_errors,
    validate_cmmn_json,
    validate_cmmn_json_file,
)


class TestSchemaLoading:
    """Test schema loading functionality."""

    def test_load_schema(self):
        """Test loading the CMMN schema."""
        schema = load_cmmn_schema()

        assert schema is not None
        assert "$schema" in schema
        assert "definitions" in schema
        assert "properties" in schema
        assert schema["properties"]["definitions"]["required"] == ["cases"]

    def test_schema_has_required_elements(self):
        """Test that schema contains all required CMMN elements."""
        schema = load_cmmn_schema()
        definitions = schema["definitions"]

        required_elements = [
            "Case",
            "CaseFileModel",
            "CaseFileItem",
            "CasePlanModel",
            "PlanItem",
            "ItemControl",
            "Stage",
            "HumanTask",
            "ProcessTask",
            "CaseTask",
            "Milestone",
            "TimerEventListener",
            "UserEventListener",
            "Sentry",
            "OnPart",
            "IfPart",
            "EntryCriterion",
            "ExitCriterion",
            "Role",
        ]

        for element in required_elements:
            assert element in definitions, f"Schema missing definition for {element}"


class TestValidationFunctions:
    """Test standalone validation functions."""

    def test_validate_minimal_valid_json(self):
        """Test validation of minimal valid CMMN JSON."""
        data = {"definitions": {"cases": [{"id": "TestCase"}]}}

        assert validate_cmmn_json(data) is True

    def test_validate_json_string(self):
        """Test validation of JSON string."""
        json_string = json.dumps(
            {"definitions": {"cases": [{"id": "TestCase", "name": "Test Case"}]}}
        )

        assert validate_cmmn_json(json_string) is True

    def test_validate_invalid_json_missing_required(self):
        """Test validation failure for missing required fields."""
        data = {
            "definitions": {
                "cases": [
                    {
                        # Missing required 'id' field
                        "name": "Test Case"
                    }
                ]
            }
        }

        with pytest.raises(CMMNParseError) as exc_info:
            validate_cmmn_json(data)

        assert "JSON validation failed" in str(exc_info.value)

    def test_validate_invalid_json_wrong_type(self):
        """Test validation failure for wrong data types."""
        data = {
            "definitions": {
                "cases": [{"id": 123, "name": "Test Case"}]  # Should be string
            }
        }

        with pytest.raises(CMMNParseError) as exc_info:
            validate_cmmn_json(data)

        assert "JSON validation failed" in str(exc_info.value)

    def test_validate_malformed_json_string(self):
        """Test validation failure for malformed JSON string."""
        malformed_json = (
            '{"definitions": {"cases": [{"id": "test"]}}'  # Missing closing brace
        )

        with pytest.raises(CMMNParseError) as exc_info:
            validate_cmmn_json(malformed_json)

        assert "Invalid JSON format" in str(exc_info.value)

    def test_validate_file_exists(self):
        """Test validation of existing JSON file."""
        fixtures_dir = Path(__file__).parent / "fixtures"
        json_file = fixtures_dir / "minimal_cmmn.json"

        assert validate_cmmn_json_file(json_file) is True

    def test_validate_file_not_found(self):
        """Test validation failure for missing file."""
        with pytest.raises(CMMNParseError) as exc_info:
            validate_cmmn_json_file("nonexistent_file.json")

        assert "File not found" in str(exc_info.value)

    def test_get_validation_errors_valid_data(self):
        """Test getting validation errors for valid data."""
        data = {"definitions": {"cases": [{"id": "TestCase", "name": "Test Case"}]}}

        errors = get_validation_errors(data)
        assert errors == []

    def test_get_validation_errors_invalid_data(self):
        """Test getting validation errors for invalid data."""
        data = {
            "definitions": {
                "cases": [
                    {
                        # Missing required 'id' field
                        "name": "Test Case"
                    }
                ]
            }
        }

        errors = get_validation_errors(data)
        assert len(errors) == 1
        assert "JSON validation failed" in errors[0]

    def test_get_validation_errors_malformed_json(self):
        """Test getting validation errors for malformed JSON."""
        malformed_json = '{"invalid": json}'

        errors = get_validation_errors(malformed_json)
        assert len(errors) == 1
        assert "Invalid JSON format" in errors[0]

    def test_get_schema_info(self):
        """Test getting schema information."""
        info = get_schema_info()

        assert isinstance(info, dict)
        assert "title" in info
        assert "description" in info
        assert "version" in info
        assert "supported_elements" in info

        assert info["title"] == "CMMN JSON Schema"
        assert isinstance(info["supported_elements"], list)
        assert len(info["supported_elements"]) > 0

        # Check that some key elements are in the supported list
        elements = info["supported_elements"]
        assert "Case" in elements
        assert "CasePlanModel" in elements
        assert "HumanTask" in elements


class TestSchemaValidationDetails:
    """Test detailed schema validation scenarios."""

    def test_validate_case_file_item_multiplicity(self):
        """Test validation of case file item multiplicity enum."""
        # Valid multiplicity
        valid_data = {
            "definitions": {
                "cases": [
                    {
                        "id": "TestCase",
                        "caseFileModel": {
                            "id": "FileModel1",
                            "caseFileItems": [
                                {"id": "Item1", "multiplicity": "OneOrMore"}
                            ],
                        },
                    }
                ]
            }
        }

        assert validate_cmmn_json(valid_data) is True

        # Invalid multiplicity
        invalid_data = {
            "definitions": {
                "cases": [
                    {
                        "id": "TestCase",
                        "caseFileModel": {
                            "id": "FileModel1",
                            "caseFileItems": [
                                {"id": "Item1", "multiplicity": "InvalidValue"}
                            ],
                        },
                    }
                ]
            }
        }

        with pytest.raises(CMMNParseError):
            validate_cmmn_json(invalid_data)

    def test_validate_standard_event_enum(self):
        """Test validation of standard event enum values."""
        # Valid standard event
        valid_data = {
            "definitions": {
                "cases": [
                    {
                        "id": "TestCase",
                        "casePlanModel": {
                            "id": "Plan1",
                            "sentries": [
                                {
                                    "id": "Sentry1",
                                    "onParts": [
                                        {"id": "OnPart1", "standardEvent": "complete"}
                                    ],
                                }
                            ],
                        },
                    }
                ]
            }
        }

        assert validate_cmmn_json(valid_data) is True

        # Invalid standard event
        invalid_data = {
            "definitions": {
                "cases": [
                    {
                        "id": "TestCase",
                        "casePlanModel": {
                            "id": "Plan1",
                            "sentries": [
                                {
                                    "id": "Sentry1",
                                    "onParts": [
                                        {
                                            "id": "OnPart1",
                                            "standardEvent": "invalid_event",
                                        }
                                    ],
                                }
                            ],
                        },
                    }
                ]
            }
        }

        with pytest.raises(CMMNParseError):
            validate_cmmn_json(invalid_data)

    def test_validate_required_id_fields(self):
        """Test validation of required ID fields across different elements."""
        elements_to_test = [
            ("cases", {"name": "Test Case"}),
            ("planItems", {"name": "Test Item"}),
            ("sentries", {"name": "Test Sentry"}),
            ("onParts", {"sourceRef": "ref"}),
            ("ifParts", {"condition": "true"}),
        ]

        for element_key, element_data in elements_to_test:
            if element_key == "cases":
                invalid_data = {"definitions": {"cases": [element_data]}}
            else:
                # Create nested structure for other elements
                invalid_data = {
                    "definitions": {
                        "cases": [{"id": "TestCase", "casePlanModel": {"id": "Plan1"}}]
                    }
                }

                if element_key == "planItems":
                    invalid_data["definitions"]["cases"][0]["casePlanModel"][
                        "planItems"
                    ] = [element_data]
                elif element_key == "sentries":
                    invalid_data["definitions"]["cases"][0]["casePlanModel"][
                        "sentries"
                    ] = [element_data]
                elif element_key == "onParts":
                    invalid_data["definitions"]["cases"][0]["casePlanModel"][
                        "sentries"
                    ] = [{"id": "Sentry1", "onParts": [element_data]}]
                elif element_key == "ifParts":
                    invalid_data["definitions"]["cases"][0]["casePlanModel"][
                        "sentries"
                    ] = [{"id": "Sentry1", "ifPart": element_data}]

            with pytest.raises(CMMNParseError) as exc_info:
                validate_cmmn_json(invalid_data)

            assert "JSON validation failed" in str(exc_info.value)

    def test_validate_nested_structures(self):
        """Test validation of deeply nested structures."""
        data = {
            "definitions": {
                "cases": [
                    {
                        "id": "NestedCase",
                        "caseFileModel": {
                            "id": "FileModel1",
                            "caseFileItems": [
                                {
                                    "id": "ParentItem",
                                    "children": [
                                        {
                                            "id": "ChildItem1",
                                            "children": [
                                                {
                                                    "id": "GrandchildItem",
                                                    "name": "Deeply nested item",
                                                }
                                            ],
                                        }
                                    ],
                                }
                            ],
                        },
                    }
                ]
            }
        }

        assert validate_cmmn_json(data) is True

    def test_validate_oneOf_task_definitions(self):
        """Test validation of oneOf constraints for task definitions."""
        # Valid task definitions with different types
        valid_data = {
            "definitions": {
                "cases": [
                    {
                        "id": "TaskCase",
                        "casePlanModel": {
                            "id": "Plan1",
                            "taskDefinitions": [
                                {
                                    "id": "HumanTask1",
                                    "name": "Human Task",
                                    "performer": "user",
                                },
                                {
                                    "id": "ProcessTask1",
                                    "name": "Process Task",
                                    "processRef": "process",
                                },
                                {
                                    "id": "CaseTask1",
                                    "name": "Case Task",
                                    "caseRef": "case",
                                },
                            ],
                        },
                    }
                ]
            }
        }

        assert validate_cmmn_json(valid_data) is True
