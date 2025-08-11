"""Tests for JSON parsing functionality."""

import json
from pathlib import Path

import pytest

import cmmn_parser
from cmmn_parser import (
    CMMNParseError,
    CMMNParser,
    get_schema_info,
    get_validation_errors,
    parse_cmmn_json,
    parse_cmmn_json_file,
    validate_cmmn_json,
    validate_cmmn_json_file,
)


class TestJSONParsing:
    """Test JSON parsing functionality."""

    def test_parse_minimal_json_string(self):
        """Test parsing a minimal CMMN JSON string."""
        json_data = {
            "definitions": {
                "cases": [
                    {
                        "id": "SimpleCase",
                        "name": "Simple Case",
                        "casePlanModel": {
                            "id": "CasePlan",
                            "name": "Case Plan",
                            "taskDefinitions": [
                                {"id": "HumanTask1", "name": "Review Document"}
                            ],
                        },
                    }
                ]
            }
        }

        parser = CMMNParser()
        definition = parser.parse_json_string(json.dumps(json_data))

        assert definition is not None
        assert len(definition.cases) == 1

        case = definition.cases[0]
        assert case.id == "SimpleCase"
        assert case.name == "Simple Case"
        assert case.case_plan_model is not None
        assert case.case_plan_model.id == "CasePlan"
        assert len(case.case_plan_model._task_definitions) == 1

        task = case.case_plan_model._task_definitions[0]
        assert task.id == "HumanTask1"
        assert task.name == "Review Document"

    def test_parse_json_file(self):
        """Test parsing a CMMN JSON file."""
        fixtures_dir = Path(__file__).parent / "fixtures"
        json_file = fixtures_dir / "minimal_cmmn.json"

        parser = CMMNParser()
        definition = parser.parse_json_file(json_file)

        assert definition is not None
        assert len(definition.cases) == 1

        case = definition.cases[0]
        assert case.id == "SimpleCase"
        assert case.name == "Simple Case"

    def test_parse_complex_json_file(self):
        """Test parsing a complex CMMN JSON file."""
        fixtures_dir = Path(__file__).parent / "fixtures"
        json_file = fixtures_dir / "sample_cmmn.json"

        parser = CMMNParser()
        definition = parser.parse_json_file(json_file)

        assert definition is not None
        assert definition.target_namespace == "http://example.com/cmmn"
        assert definition.exporter == "TestExporter"
        assert len(definition.cases) == 1

        case = definition.cases[0]
        assert case.id == "Case_1"
        assert case.name == "Test Case"

        # Check case file model
        assert case.case_file_model is not None
        assert len(case.case_file_model.case_file_items) == 2

        # Check nested case file items
        doc_item = case.case_file_model.case_file_items[0]
        assert doc_item.name == "Document"
        assert len(doc_item.children) == 1
        assert doc_item.children[0].name == "Attachment"

        # Check case plan model
        assert case.case_plan_model is not None
        assert case.case_plan_model.auto_complete is True
        assert len(case.case_plan_model.plan_items) == 7

        # Check plan item with item control
        plan_item = case.case_plan_model.plan_items[0]
        assert plan_item.name == "Initial Stage"
        assert plan_item.item_control is not None
        assert plan_item.item_control.required_rule == "true"

        # Check sentries
        assert len(case.case_plan_model.sentries) == 2
        sentry = case.case_plan_model.sentries[0]
        assert sentry.name == "Entry Sentry"
        assert len(sentry.on_parts) == 1
        assert sentry.if_part is not None

        # Check task definitions
        assert len(case.case_plan_model._task_definitions) == 4
        human_task = case.case_plan_model._task_definitions[0]
        assert human_task.name == "Review Document"
        assert human_task.performer == "reviewer"

        # Check event definitions
        assert len(case.case_plan_model._event_definitions) == 2
        timer_event = case.case_plan_model._event_definitions[0]
        assert timer_event.timer_expression == "PT2H"

        # Check roles
        assert len(case.case_roles) == 3
        assert case.case_roles[0].name == "reviewer"

    def test_auto_detect_json_format(self):
        """Test auto-detection of JSON format in generic parse methods."""
        json_data = {
            "definitions": {"cases": [{"id": "TestCase", "name": "Test Case"}]}
        }

        parser = CMMNParser()
        definition = parser.parse_string(json.dumps(json_data))

        assert definition is not None
        assert len(definition.cases) == 1
        assert definition.cases[0].id == "TestCase"

    def test_auto_detect_json_file(self):
        """Test auto-detection of JSON format when parsing files."""
        fixtures_dir = Path(__file__).parent / "fixtures"
        json_file = fixtures_dir / "minimal_cmmn.json"

        parser = CMMNParser()
        definition = parser.parse_file(json_file)

        assert definition is not None
        assert len(definition.cases) == 1
        assert definition.cases[0].id == "SimpleCase"

    def test_invalid_json_format(self):
        """Test error handling for invalid JSON."""
        parser = CMMNParser()

        with pytest.raises(CMMNParseError, match="Invalid JSON format"):
            parser.parse_json_string('{"invalid": json}')

    def test_json_schema_validation_failure(self):
        """Test schema validation failure."""
        invalid_data = {
            "definitions": {
                "cases": [
                    {
                        # Missing required 'id' field
                        "name": "Test Case"
                    }
                ]
            }
        }

        parser = CMMNParser()
        with pytest.raises(CMMNParseError, match="JSON validation failed"):
            parser.parse_json_string(json.dumps(invalid_data))

    def test_file_not_found(self):
        """Test error handling for missing files."""
        parser = CMMNParser()

        with pytest.raises(CMMNParseError, match="CMMN file not found"):
            parser.parse_json_file("nonexistent.json")


class TestConvenienceFunctions:
    """Test convenience functions for JSON parsing."""

    def test_parse_cmmn_json_dict(self):
        """Test parse_cmmn_json with dictionary input."""
        json_data = {
            "definitions": {"cases": [{"id": "TestCase", "name": "Test Case"}]}
        }

        definition = parse_cmmn_json(json_data)

        assert definition is not None
        assert len(definition.cases) == 1
        assert definition.cases[0].id == "TestCase"

    def test_parse_cmmn_json_string(self):
        """Test parse_cmmn_json with string input."""
        json_string = (
            '{"definitions": {"cases": [{"id": "TestCase", "name": "Test Case"}]}}'
        )

        definition = parse_cmmn_json(json_string)

        assert definition is not None
        assert len(definition.cases) == 1
        assert definition.cases[0].id == "TestCase"

    def test_parse_cmmn_json_file(self):
        """Test parse_cmmn_json_file convenience function."""
        fixtures_dir = Path(__file__).parent / "fixtures"
        json_file = fixtures_dir / "minimal_cmmn.json"

        definition = parse_cmmn_json_file(json_file)

        assert definition is not None
        assert len(definition.cases) == 1
        assert definition.cases[0].id == "SimpleCase"


class TestJSONValidation:
    """Test JSON validation functionality."""

    def test_validate_valid_json(self):
        """Test validation of valid CMMN JSON."""
        json_data = {
            "definitions": {"cases": [{"id": "TestCase", "name": "Test Case"}]}
        }

        assert validate_cmmn_json(json_data) is True

    def test_validate_valid_json_string(self):
        """Test validation of valid CMMN JSON string."""
        json_string = (
            '{"definitions": {"cases": [{"id": "TestCase", "name": "Test Case"}]}}'
        )

        assert validate_cmmn_json(json_string) is True

    def test_validate_invalid_json(self):
        """Test validation of invalid CMMN JSON."""
        invalid_data = {
            "definitions": {
                "cases": [
                    {
                        # Missing required 'id' field
                        "name": "Test Case"
                    }
                ]
            }
        }

        with pytest.raises(CMMNParseError, match="JSON validation failed"):
            validate_cmmn_json(invalid_data)

    def test_validate_malformed_json_string(self):
        """Test validation of malformed JSON string."""
        with pytest.raises(CMMNParseError, match="Invalid JSON format"):
            validate_cmmn_json('{"invalid": json}')

    def test_validate_json_file(self):
        """Test validation of CMMN JSON file."""
        fixtures_dir = Path(__file__).parent / "fixtures"
        json_file = fixtures_dir / "minimal_cmmn.json"

        assert validate_cmmn_json_file(json_file) is True

    def test_validate_missing_file(self):
        """Test validation of missing file."""
        with pytest.raises(CMMNParseError, match="File not found"):
            validate_cmmn_json_file("nonexistent.json")

    def test_get_validation_errors_valid(self):
        """Test getting validation errors for valid data."""
        json_data = {
            "definitions": {"cases": [{"id": "TestCase", "name": "Test Case"}]}
        }

        errors = get_validation_errors(json_data)
        assert errors == []

    def test_get_validation_errors_invalid(self):
        """Test getting validation errors for invalid data."""
        invalid_data = {
            "definitions": {
                "cases": [
                    {
                        # Missing required 'id' field
                        "name": "Test Case"
                    }
                ]
            }
        }

        errors = get_validation_errors(invalid_data)
        assert len(errors) > 0
        assert "JSON validation failed" in errors[0]

    def test_get_schema_info(self):
        """Test getting schema information."""
        info = get_schema_info()

        assert "title" in info
        assert "description" in info
        assert "supported_elements" in info
        assert isinstance(info["supported_elements"], list)
        assert len(info["supported_elements"]) > 0


class TestJSONSpecificFeatures:
    """Test JSON-specific features and edge cases."""

    def test_parse_json_with_all_optional_fields(self):
        """Test parsing JSON with all optional fields populated."""
        json_data = {
            "definitions": {
                "targetNamespace": "http://example.com/test",
                "expressionLanguage": "http://www.w3.org/1999/XPath",
                "exporter": "TestTool",
                "exporterVersion": "2.0.0",
                "cases": [
                    {
                        "id": "FullCase",
                        "name": "Full Case",
                        "documentation": "A fully documented case",
                    }
                ],
            }
        }

        definition = parse_cmmn_json(json_data)

        assert definition.target_namespace == "http://example.com/test"
        assert definition.expression_language == "http://www.w3.org/1999/XPath"
        assert definition.exporter == "TestTool"
        assert definition.exporter_version == "2.0.0"

        case = definition.cases[0]
        assert case.documentation == "A fully documented case"

    def test_parse_empty_arrays(self):
        """Test parsing JSON with empty arrays."""
        json_data = {
            "definitions": {
                "cases": [
                    {
                        "id": "EmptyCase",
                        "name": "Empty Case",
                        "casePlanModel": {
                            "id": "EmptyPlan",
                            "planItems": [],
                            "sentries": [],
                            "caseFileItems": [],
                            "taskDefinitions": [],
                            "eventDefinitions": [],
                            "milestoneDefinitions": [],
                            "stageDefinitions": [],
                            "criteriaDefinitions": [],
                        },
                        "caseRoles": [],
                    }
                ]
            }
        }

        definition = parse_cmmn_json(json_data)

        assert definition is not None
        case = definition.cases[0]
        plan = case.case_plan_model

        assert len(plan.plan_items) == 0
        assert len(plan.sentries) == 0
        assert len(plan.case_file_items) == 0
        assert len(plan._task_definitions) == 0
        assert len(plan._event_definitions) == 0
        assert len(plan._milestone_definitions) == 0
        assert len(plan._stage_definitions) == 0
        assert len(plan._criteria_definitions) == 0
        assert len(case.case_roles) == 0

    def test_criterion_type_detection(self):
        """Test criterion type detection in JSON."""
        json_data = {
            "definitions": {
                "cases": [
                    {
                        "id": "CriterionCase",
                        "casePlanModel": {
                            "id": "CriterionPlan",
                            "criteriaDefinitions": [
                                {
                                    "id": "EntryCrit1",
                                    "name": "Entry Criterion",
                                    "sentryRef": "Sentry1",
                                    "type": "entry",
                                },
                                {
                                    "id": "ExitCrit1",
                                    "name": "Exit Criterion",
                                    "sentryRef": "Sentry2",
                                    "type": "exit",
                                },
                            ],
                        },
                    }
                ]
            }
        }

        definition = parse_cmmn_json(json_data)
        criteria = definition.cases[0].case_plan_model._criteria_definitions

        assert len(criteria) == 2

        # Check that we get the right criterion types
        entry_criterion = next(c for c in criteria if c.id == "EntryCrit1")
        exit_criterion = next(c for c in criteria if c.id == "ExitCrit1")

        from cmmn_parser.models import EntryCriterion, ExitCriterion

        assert isinstance(entry_criterion, EntryCriterion)
        assert isinstance(exit_criterion, ExitCriterion)

    def test_task_type_detection(self):
        """Test task type detection based on fields in JSON."""
        json_data = {
            "definitions": {
                "cases": [
                    {
                        "id": "TaskCase",
                        "casePlanModel": {
                            "id": "TaskPlan",
                            "taskDefinitions": [
                                {
                                    "id": "HumanTask1",
                                    "name": "Human Task",
                                    "performer": "user",
                                },
                                {
                                    "id": "ProcessTask1",
                                    "name": "Process Task",
                                    "processRef": "SomeProcess",
                                },
                                {
                                    "id": "CaseTask1",
                                    "name": "Case Task",
                                    "caseRef": "SomeCase",
                                },
                            ],
                        },
                    }
                ]
            }
        }

        definition = parse_cmmn_json(json_data)
        tasks = definition.cases[0].case_plan_model._task_definitions

        assert len(tasks) == 3

        from cmmn_parser.models import CaseTask, HumanTask, ProcessTask

        human_task = next(t for t in tasks if t.id == "HumanTask1")
        process_task = next(t for t in tasks if t.id == "ProcessTask1")
        case_task = next(t for t in tasks if t.id == "CaseTask1")

        assert isinstance(human_task, HumanTask)
        assert isinstance(process_task, ProcessTask)
        assert isinstance(case_task, CaseTask)

        assert human_task.performer == "user"
        assert process_task.process_ref == "SomeProcess"
        assert case_task.case_ref == "SomeCase"
