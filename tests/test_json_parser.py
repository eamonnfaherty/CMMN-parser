"""Tests for CMMN JSON parser functionality."""

import pytest

from cmmn_parser.exceptions import CMMNParsingError
from cmmn_parser.json_parser import JSONParser
from cmmn_parser.models import (
    Case,
    CasePlanModel,
    CaseTask,
    CMMNDefinitions,
    DecisionTask,
    HumanTask,
    Import,
    Milestone,
    PlanItem,
    ProcessTask,
    Sentry,
    Stage,
    Task,
)


class TestJSONParser:
    """Test JSON parser functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = JSONParser()

    def test_parser_initialization(self):
        """Test parser initialization."""
        parser = JSONParser()
        assert parser is not None

    def test_parse_non_dict_raises_error(self):
        """Test parsing non-dictionary data raises error."""
        with pytest.raises(CMMNParsingError, match="JSON data must be a dictionary"):
            self.parser.parse("not a dict")

        with pytest.raises(CMMNParsingError, match="JSON data must be a dictionary"):
            self.parser.parse([1, 2, 3])

    def test_parse_basic_definitions(self):
        """Test parsing basic definitions."""
        data = {
            "id": "def1",
            "name": "Test Definitions",
            "targetNamespace": "http://example.com",
            "exporter": "test",
            "exporterVersion": "1.0",
            "author": "test author",
            "creationDate": "2023-01-01",
        }

        result = self.parser.parse(data)
        assert isinstance(result, CMMNDefinitions)
        assert result.id == "def1"
        assert result.name == "Test Definitions"
        assert result.target_namespace == "http://example.com"
        assert result.exporter == "test"
        assert result.exporter_version == "1.0"
        assert result.author == "test author"
        assert result.creation_date == "2023-01-01"

    def test_parse_import(self):
        """Test parsing import element."""
        data = {
            "imports": [
                {
                    "id": "import1",
                    "namespace": "http://example.com",
                    "location": "example.xsd",
                    "importType": "http://example.com/type",
                }
            ]
        }

        result = self.parser.parse(data)
        assert len(result.imports) == 1
        import_obj = result.imports[0]
        assert import_obj.id == "import1"
        assert import_obj.namespace == "http://example.com"
        assert import_obj.location == "example.xsd"
        assert import_obj.import_type == "http://example.com/type"

    def test_parse_case_file_item_definition(self):
        """Test parsing case file item definition."""
        data = {
            "caseFileItemDefinitions": [
                {
                    "id": "cfid1",
                    "name": "Test Item",
                    "description": "Test description",
                    "structureRef": "struct1",
                    "definitiveProperty": ["prop1", "prop2"],
                }
            ]
        }

        result = self.parser.parse(data)
        assert len(result.case_file_item_definitions) == 1
        cfid = result.case_file_item_definitions[0]
        assert cfid.id == "cfid1"
        assert cfid.name == "Test Item"
        assert cfid.description == "Test description"
        assert cfid.structure_ref == "struct1"
        assert len(cfid.definitive_property) == 2
        assert "prop1" in cfid.definitive_property
        assert "prop2" in cfid.definitive_property

    def test_parse_basic_case(self):
        """Test parsing basic case."""
        data = {
            "cases": [
                {
                    "id": "case1",
                    "name": "Test Case",
                    "description": "Test case description",
                }
            ]
        }

        result = self.parser.parse(data)
        assert len(result.cases) == 1
        case = result.cases[0]
        assert case.id == "case1"
        assert case.name == "Test Case"
        assert case.description == "Test case description"
        assert case.case_plan_model is None

    def test_parse_case_with_plan_model(self):
        """Test parsing case with case plan model."""
        data = {
            "cases": [
                {
                    "id": "case1",
                    "name": "Test Case",
                    "casePlanModel": {
                        "id": "cpm1",
                        "name": "Case Plan Model",
                        "autoComplete": True,
                    },
                }
            ]
        }

        result = self.parser.parse(data)
        case = result.cases[0]
        assert case.case_plan_model is not None
        cpm = case.case_plan_model
        assert cpm.id == "cpm1"
        assert cpm.name == "Case Plan Model"
        assert cpm.auto_complete is True

    def test_parse_case_file_model(self):
        """Test parsing case file model."""
        data = {
            "cases": [
                {
                    "id": "case1",
                    "name": "Test Case",
                    "caseFileModel": {
                        "id": "cfm1",
                        "name": "Case File Model",
                        "caseFileItems": ["item1", "item2"],
                    },
                }
            ]
        }

        result = self.parser.parse(data)
        case = result.cases[0]
        assert case.case_file_model is not None
        cfm = case.case_file_model
        assert cfm.id == "cfm1"
        assert cfm.name == "Case File Model"
        assert len(cfm.case_file_items) == 2
        assert "item1" in cfm.case_file_items
        assert "item2" in cfm.case_file_items

    def test_parse_task_elements(self):
        """Test parsing different task elements."""
        data = {
            "cases": [
                {
                    "id": "case1",
                    "name": "Test Case",
                    "casePlanModel": {
                        "id": "cpm1",
                        "name": "Case Plan Model",
                        "tasks": [
                            {
                                "id": "task1",
                                "name": "Basic Task",
                                "isBlocking": False,
                                "type": "task",
                            },
                            {
                                "id": "task2",
                                "name": "Human Task",
                                "type": "humanTask",
                                "performer": "user1",
                                "formKey": "form1",
                            },
                            {
                                "id": "task3",
                                "name": "Process Task",
                                "type": "processTask",
                                "processRef": "process1",
                            },
                            {
                                "id": "task4",
                                "name": "Case Task",
                                "type": "caseTask",
                                "caseRef": "case1",
                            },
                            {
                                "id": "task5",
                                "name": "Decision Task",
                                "type": "decisionTask",
                                "decisionRef": "decision1",
                            },
                        ],
                    },
                }
            ]
        }

        result = self.parser.parse(data)
        cpm = result.cases[0].case_plan_model
        assert len(cpm.tasks) == 5

        task1 = cpm.tasks[0]
        assert task1.id == "task1"
        assert task1.name == "Basic Task"
        assert task1.is_blocking is False
        assert isinstance(task1, Task)

        task2 = cpm.tasks[1]
        assert isinstance(task2, HumanTask)
        assert task2.performer == "user1"
        assert task2.form_key == "form1"

        task3 = cpm.tasks[2]
        assert isinstance(task3, ProcessTask)
        assert task3.process_ref == "process1"

        task4 = cpm.tasks[3]
        assert isinstance(task4, CaseTask)
        assert task4.case_ref == "case1"

        task5 = cpm.tasks[4]
        assert isinstance(task5, DecisionTask)
        assert task5.decision_ref == "decision1"

    def test_parse_milestone(self):
        """Test parsing milestone element."""
        data = {
            "cases": [
                {
                    "id": "case1",
                    "name": "Test Case",
                    "casePlanModel": {
                        "id": "cpm1",
                        "name": "Case Plan Model",
                        "milestones": [
                            {
                                "id": "milestone1",
                                "name": "Test Milestone",
                                "description": "Milestone description",
                            }
                        ],
                    },
                }
            ]
        }

        result = self.parser.parse(data)
        cpm = result.cases[0].case_plan_model
        assert len(cpm.milestones) == 1
        milestone = cpm.milestones[0]
        assert milestone.id == "milestone1"
        assert milestone.name == "Test Milestone"
        assert milestone.description == "Milestone description"

    def test_parse_stage(self):
        """Test parsing stage element."""
        data = {
            "cases": [
                {
                    "id": "case1",
                    "name": "Test Case",
                    "casePlanModel": {
                        "id": "cpm1",
                        "name": "Case Plan Model",
                        "stages": [
                            {
                                "id": "stage1",
                                "name": "Test Stage",
                                "autoComplete": True,
                                "planItems": [
                                    {
                                        "id": "pi1",
                                        "name": "Plan Item 1",
                                        "definitionRef": "task1",
                                    }
                                ],
                            }
                        ],
                    },
                }
            ]
        }

        result = self.parser.parse(data)
        cpm = result.cases[0].case_plan_model
        assert len(cpm.stages) == 1
        stage = cpm.stages[0]
        assert stage.id == "stage1"
        assert stage.name == "Test Stage"
        assert stage.auto_complete is True
        assert len(stage.plan_items) == 1
        assert stage.plan_items[0].id == "pi1"

    def test_parse_plan_item(self):
        """Test parsing plan item element."""
        data = {
            "cases": [
                {
                    "id": "case1",
                    "name": "Test Case",
                    "casePlanModel": {
                        "id": "cpm1",
                        "name": "Case Plan Model",
                        "planItems": [
                            {
                                "id": "pi1",
                                "name": "Plan Item 1",
                                "definitionRef": "task1",
                                "entryCriteria": ["sentry1"],
                                "exitCriteria": ["sentry2"],
                            }
                        ],
                    },
                }
            ]
        }

        result = self.parser.parse(data)
        cpm = result.cases[0].case_plan_model
        assert len(cpm.plan_items) == 1
        plan_item = cpm.plan_items[0]
        assert plan_item.id == "pi1"
        assert plan_item.name == "Plan Item 1"
        assert plan_item.definition_ref == "task1"
        assert len(plan_item.entry_criteria) == 1
        assert plan_item.entry_criteria[0] == "sentry1"
        assert len(plan_item.exit_criteria) == 1
        assert plan_item.exit_criteria[0] == "sentry2"

    def test_parse_sentry(self):
        """Test parsing sentry element."""
        data = {
            "cases": [
                {
                    "id": "case1",
                    "name": "Test Case",
                    "casePlanModel": {
                        "id": "cpm1",
                        "name": "Case Plan Model",
                        "sentries": [
                            {
                                "id": "sentry1",
                                "name": "Test Sentry",
                                "onPart": ["task1", "task2"],
                                "ifPart": "condition expression",
                            }
                        ],
                    },
                }
            ]
        }

        result = self.parser.parse(data)
        cpm = result.cases[0].case_plan_model
        assert len(cpm.sentries) == 1
        sentry = cpm.sentries[0]
        assert sentry.id == "sentry1"
        assert sentry.name == "Test Sentry"
        assert len(sentry.on_part) == 2
        assert "task1" in sentry.on_part
        assert "task2" in sentry.on_part
        assert sentry.if_part == "condition expression"

    def test_parse_process(self):
        """Test parsing process element."""
        data = {
            "processes": [
                {
                    "id": "process1",
                    "name": "Test Process",
                    "description": "Process description",
                    "isExecutable": False,
                    "implementationType": "custom",
                }
            ]
        }

        result = self.parser.parse(data)
        assert len(result.processes) == 1
        process = result.processes[0]
        assert process.id == "process1"
        assert process.name == "Test Process"
        assert process.description == "Process description"
        assert process.is_executable is False
        assert process.implementation_type == "custom"

    def test_parse_decision(self):
        """Test parsing decision element."""
        data = {
            "decisions": [
                {
                    "id": "decision1",
                    "name": "Test Decision",
                    "description": "Decision description",
                    "decisionLogic": "decision logic content",
                }
            ]
        }

        result = self.parser.parse(data)
        assert len(result.decisions) == 1
        decision = result.decisions[0]
        assert decision.id == "decision1"
        assert decision.name == "Test Decision"
        assert decision.description == "Decision description"
        assert decision.decision_logic == "decision logic content"

    def test_parse_extension_elements(self):
        """Test parsing extension elements."""
        data = {
            "extensionElements": {
                "custom": {"attr": "value", "content": "data"},
                "another": {"nested": {"value": "test"}},
            }
        }

        result = self.parser.parse(data)
        assert result.extension_elements is not None
        elements = result.extension_elements.elements
        assert "custom" in elements
        assert elements["custom"]["attr"] == "value"
        assert elements["custom"]["content"] == "data"
        assert "another" in elements
        assert elements["another"]["nested"]["value"] == "test"

    def test_parse_task_with_tasktype_fallback(self):
        """Test parsing task with taskType instead of type."""
        data = {
            "cases": [
                {
                    "id": "case1",
                    "name": "Test Case",
                    "casePlanModel": {
                        "id": "cpm1",
                        "name": "Case Plan Model",
                        "tasks": [
                            {
                                "id": "task1",
                                "name": "Task with taskType",
                                "taskType": "customTask",
                            }
                        ],
                    },
                }
            ]
        }

        result = self.parser.parse(data)
        cpm = result.cases[0].case_plan_model
        task = cpm.tasks[0]
        assert task.task_type == "customTask"

    def test_parse_empty_arrays(self):
        """Test parsing with empty arrays."""
        data = {"imports": [], "cases": [], "processes": [], "decisions": []}

        result = self.parser.parse(data)
        assert len(result.imports) == 0
        assert len(result.cases) == 0
        assert len(result.processes) == 0
        assert len(result.decisions) == 0

    def test_parse_missing_optional_fields(self):
        """Test parsing with missing optional fields."""
        data = {
            "id": "def1",
            "cases": [
                {
                    "id": "case1",
                    "casePlanModel": {
                        "id": "cpm1",
                        "planItems": [{"id": "pi1"}],
                        "tasks": [{"id": "task1"}],
                    },
                }
            ],
        }

        result = self.parser.parse(data)
        assert result.id == "def1"
        assert result.name is None

        case = result.cases[0]
        assert case.name is None

        plan_item = case.case_plan_model.plan_items[0]
        assert plan_item.definition_ref is None
        assert len(plan_item.entry_criteria) == 0

        task = case.case_plan_model.tasks[0]
        assert task.is_blocking is True  # default value
