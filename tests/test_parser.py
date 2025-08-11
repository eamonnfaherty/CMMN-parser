import os
import tempfile
from pathlib import Path

import pytest

from cmmn_parser import CMMNParseError, CMMNParser
from cmmn_parser.models import (
    Case,
    CaseFileItem,
    CaseFileModel,
    CasePlanModel,
    CaseTask,
    CMMNDefinition,
    CMMNElementType,
    EntryCriterion,
    ExitCriterion,
    HumanTask,
    IfPart,
    ItemControl,
    Milestone,
    OnPart,
    PlanItem,
    ProcessTask,
    Role,
    Sentry,
    Stage,
    TimerEventListener,
    UserEventListener,
)


class TestCMMNParser:

    @pytest.fixture
    def parser(self):
        return CMMNParser()

    @pytest.fixture
    def sample_cmmn_file(self):
        return Path(__file__).parent / "fixtures" / "sample_cmmn.xml"

    @pytest.fixture
    def minimal_cmmn_file(self):
        return Path(__file__).parent / "fixtures" / "minimal_cmmn.xml"

    @pytest.fixture
    def sample_cmmn_content(self, sample_cmmn_file):
        return sample_cmmn_file.read_text()

    def test_parse_file_basic(self, parser, sample_cmmn_file):
        """Test basic file parsing functionality."""
        definition = parser.parse_file(sample_cmmn_file)

        assert isinstance(definition, CMMNDefinition)
        assert definition.target_namespace == "http://example.com/cmmn"
        assert definition.expression_language == "http://www.w3.org/1999/XPath"
        assert definition.exporter == "TestExporter"
        assert definition.exporter_version == "1.0.0"
        assert len(definition.cases) == 1

    def test_parse_string_basic(self, parser, sample_cmmn_content):
        """Test basic string parsing functionality."""
        definition = parser.parse_string(sample_cmmn_content)

        assert isinstance(definition, CMMNDefinition)
        assert definition.target_namespace == "http://example.com/cmmn"
        assert len(definition.cases) == 1

    def test_parse_minimal_cmmn(self, parser, minimal_cmmn_file):
        """Test parsing of minimal CMMN structure."""
        definition = parser.parse_file(minimal_cmmn_file)

        assert isinstance(definition, CMMNDefinition)
        assert definition.target_namespace == "http://example.com/minimal"
        assert definition.expression_language is None
        assert definition.exporter is None
        assert len(definition.cases) == 1

        case = definition.cases[0]
        assert case.id == "MinimalCase"
        assert case.name is None
        assert case.case_plan_model.id == "MinimalPlan"

    def test_case_parsing_complete(self, parser, sample_cmmn_file):
        """Test complete case parsing with all attributes."""
        definition = parser.parse_file(sample_cmmn_file)
        case = definition.cases[0]

        assert case.id == "Case_1"
        assert case.name == "Test Case"
        assert case.element_type == CMMNElementType.CASE
        assert case.case_file_model is not None
        assert case.case_plan_model is not None
        assert len(case.case_roles) == 3

    def test_case_file_model_parsing(self, parser, sample_cmmn_file):
        """Test case file model parsing with nested items."""
        definition = parser.parse_file(sample_cmmn_file)
        case = definition.cases[0]
        file_model = case.case_file_model

        assert file_model.id == "CaseFileModel_1"
        assert len(file_model.case_file_items) == 2

        # Test first case file item with children
        item1 = file_model.case_file_items[0]
        assert item1.id == "CaseFileItem_1"
        assert item1.name == "Document"
        assert item1.definition_type == "http://example.com/Document"
        assert item1.multiplicity == "OneOrMore"
        assert len(item1.children) == 1
        assert item1.element_type == CMMNElementType.CASE_FILE_ITEM

        # Test nested case file item
        child_item = item1.children[0]
        assert child_item.id == "CaseFileItem_2"
        assert child_item.name == "Attachment"
        assert child_item.definition_type == "http://example.com/Attachment"

        # Test second case file item with references
        item2 = file_model.case_file_items[1]
        assert item2.id == "CaseFileItem_3"
        assert item2.name == "Customer"
        assert item2.source_ref == "external_source"
        assert item2.target_refs == ["target1", "target2"]

    def test_case_plan_model_parsing(self, parser, sample_cmmn_file):
        """Test case plan model parsing."""
        definition = parser.parse_file(sample_cmmn_file)
        case = definition.cases[0]
        plan_model = case.case_plan_model

        assert plan_model.id == "CasePlanModel_1"
        assert plan_model.name == "Main Case Plan"
        assert plan_model.auto_complete is True
        assert len(plan_model.plan_items) == 7
        assert len(plan_model.sentries) == 2

    def test_plan_items_parsing(self, parser, sample_cmmn_file):
        """Test plan item parsing with item controls."""
        definition = parser.parse_file(sample_cmmn_file)
        plan_model = definition.cases[0].case_plan_model

        # Test plan item with full item control
        plan_item = plan_model.plan_items[0]
        assert plan_item.id == "PlanItem_1"
        assert plan_item.name == "Initial Stage"
        assert plan_item.definition_ref == "Stage_1"
        assert plan_item.entry_criteria == ["EntryCriterion_1"]
        assert plan_item.exit_criteria == ["ExitCriterion_1"]

        # Test item control
        item_control = plan_item.item_control
        assert item_control is not None
        assert item_control.required_rule == "true"
        assert item_control.repetition_rule == "count < 3"
        assert item_control.manual_activation_rule == "userRequested"

        # Test simple plan item
        simple_item = plan_model.plan_items[1]
        assert simple_item.id == "PlanItem_2"
        assert simple_item.name == "Human Task Item"
        assert simple_item.definition_ref == "HumanTask_1"
        assert simple_item.item_control is None

    def test_human_task_parsing(self, parser, sample_cmmn_file):
        """Test human task parsing with performer."""
        definition = parser.parse_file(sample_cmmn_file)
        plan_model = definition.cases[0].case_plan_model

        # Access task definitions from the parser
        assert hasattr(plan_model, "_task_definitions")
        task_definitions = plan_model._task_definitions

        # Find human tasks
        human_tasks = [t for t in task_definitions if isinstance(t, HumanTask)]
        assert len(human_tasks) == 2

        # Test first human task with performer
        human_task_1 = next(t for t in human_tasks if t.id == "HumanTask_1")
        assert human_task_1.name == "Review Document"
        assert human_task_1.performer == "reviewer"
        assert human_task_1.is_blocking is True
        assert human_task_1.element_type == CMMNElementType.HUMAN_TASK

        # Test second human task
        human_task_2 = next(t for t in human_tasks if t.id == "HumanTask_2")
        assert human_task_2.name == "Nested Human Task"
        assert human_task_2.is_blocking is False

    def test_process_task_parsing(self, parser, sample_cmmn_file):
        """Test process task parsing."""
        definition = parser.parse_file(sample_cmmn_file)
        plan_model = definition.cases[0].case_plan_model

        task_definitions = plan_model._task_definitions
        process_tasks = [t for t in task_definitions if isinstance(t, ProcessTask)]
        assert len(process_tasks) == 1

        process_task = process_tasks[0]
        assert process_task.id == "ProcessTask_1"
        assert process_task.name == "Automated Processing"
        assert process_task.process_ref == "AutomationProcess"
        assert process_task.is_blocking is True
        assert process_task.element_type == CMMNElementType.PROCESS_TASK

    def test_case_task_parsing(self, parser, sample_cmmn_file):
        """Test case task parsing."""
        definition = parser.parse_file(sample_cmmn_file)
        plan_model = definition.cases[0].case_plan_model

        task_definitions = plan_model._task_definitions
        case_tasks = [t for t in task_definitions if isinstance(t, CaseTask)]
        assert len(case_tasks) == 1

        case_task = case_tasks[0]
        assert case_task.id == "CaseTask_1"
        assert case_task.name == "Sub Case"
        assert case_task.case_ref == "SubCase"
        assert case_task.is_blocking is True
        assert case_task.element_type == CMMNElementType.CASE_TASK

    def test_timer_event_listener_parsing(self, parser, sample_cmmn_file):
        """Test timer event listener parsing."""
        definition = parser.parse_file(sample_cmmn_file)
        plan_model = definition.cases[0].case_plan_model

        assert hasattr(plan_model, "_event_definitions")
        event_definitions = plan_model._event_definitions

        timer_events = [
            e for e in event_definitions if isinstance(e, TimerEventListener)
        ]
        assert len(timer_events) == 1

        timer_event = timer_events[0]
        assert timer_event.id == "TimerEvent_1"
        assert timer_event.name == "Deadline Timer"
        assert timer_event.timer_expression == "PT2H"
        assert timer_event.element_type == CMMNElementType.TIMER_EVENT_LISTENER

    def test_user_event_listener_parsing(self, parser, sample_cmmn_file):
        """Test user event listener parsing."""
        definition = parser.parse_file(sample_cmmn_file)
        plan_model = definition.cases[0].case_plan_model

        event_definitions = plan_model._event_definitions
        user_events = [e for e in event_definitions if isinstance(e, UserEventListener)]
        assert len(user_events) == 1

        user_event = user_events[0]
        assert user_event.id == "UserEvent_1"
        assert user_event.name == "User Intervention"
        assert user_event.authorized_role_refs == ["admin", "manager"]
        assert user_event.element_type == CMMNElementType.USER_EVENT_LISTENER

    def test_milestone_parsing(self, parser, sample_cmmn_file):
        """Test milestone parsing."""
        definition = parser.parse_file(sample_cmmn_file)
        plan_model = definition.cases[0].case_plan_model

        assert hasattr(plan_model, "_milestone_definitions")
        milestone_definitions = plan_model._milestone_definitions

        assert len(milestone_definitions) == 1
        milestone = milestone_definitions[0]
        assert milestone.id == "Milestone_1"
        assert milestone.name == "Process Complete"
        assert milestone.element_type == CMMNElementType.MILESTONE

    def test_sentry_parsing_with_on_parts_and_if_parts(self, parser, sample_cmmn_file):
        """Test sentry parsing with on-parts and if-parts."""
        definition = parser.parse_file(sample_cmmn_file)
        plan_model = definition.cases[0].case_plan_model

        # Test first sentry with both on-part and if-part
        sentry1 = plan_model.sentries[0]
        assert sentry1.id == "Sentry_1"
        assert sentry1.name == "Entry Sentry"
        assert sentry1.element_type == CMMNElementType.SENTRY

        # Test on-part
        assert len(sentry1.on_parts) == 1
        on_part = sentry1.on_parts[0]
        assert on_part.id == "OnPart_1"
        assert on_part.source_ref == "PlanItem_2"
        assert on_part.standard_event == "complete"

        # Test if-part
        assert sentry1.if_part is not None
        if_part = sentry1.if_part
        assert if_part.id == "IfPart_1"
        assert if_part.condition == "status == 'approved'"

        # Test second sentry with only on-part
        sentry2 = plan_model.sentries[1]
        assert sentry2.id == "Sentry_2"
        assert sentry2.name == "Exit Sentry"
        assert len(sentry2.on_parts) == 1
        assert sentry2.if_part is None

        on_part2 = sentry2.on_parts[0]
        assert on_part2.source_ref == "PlanItem_5"
        assert on_part2.standard_event == "occur"

    def test_nested_stage_parsing(self, parser, sample_cmmn_file):
        """Test nested stage parsing."""
        definition = parser.parse_file(sample_cmmn_file)
        plan_model = definition.cases[0].case_plan_model

        assert hasattr(plan_model, "_stage_definitions")
        stage_definitions = plan_model._stage_definitions

        assert len(stage_definitions) == 1
        nested_stage = stage_definitions[0]
        assert nested_stage.id == "Stage_1"
        assert nested_stage.name == "Nested Stage"
        assert nested_stage.auto_complete is False
        assert nested_stage.element_type == CMMNElementType.STAGE

        # Test that nested stage has plan items
        assert len(nested_stage.plan_items) == 1
        nested_plan_item = nested_stage.plan_items[0]
        assert nested_plan_item.id == "PlanItem_8"
        assert nested_plan_item.name == "Nested Task"
        assert nested_plan_item.definition_ref == "HumanTask_2"

    def test_case_roles_parsing(self, parser, sample_cmmn_file):
        """Test case roles parsing."""
        definition = parser.parse_file(sample_cmmn_file)
        case = definition.cases[0]

        assert len(case.case_roles) == 3

        role1 = case.case_roles[0]
        assert role1.id == "Role_1"
        assert role1.name == "reviewer"

        role2 = case.case_roles[1]
        assert role2.id == "Role_2"
        assert role2.name == "admin"

        role3 = case.case_roles[2]
        assert role3.id == "Role_3"
        assert role3.name == "manager"

    def test_error_handling_invalid_xml(self, parser):
        """Test error handling for invalid XML."""
        invalid_xml = "<invalid>xml without closing tag"

        with pytest.raises(CMMNParseError, match="Failed to parse CMMN text"):
            parser.parse_string(invalid_xml)

    def test_error_handling_non_cmmn_xml(self, parser):
        """Test error handling for non-CMMN XML."""
        non_cmmn_xml = """<?xml version="1.0"?>
        <root>
            <element>This is not CMMN</element>
        </root>"""

        with pytest.raises(CMMNParseError, match="Root element must be 'definitions'"):
            parser.parse_string(non_cmmn_xml)

    def test_error_handling_file_not_found(self, parser):
        """Test error handling for non-existent files."""
        with pytest.raises(CMMNParseError, match="CMMN file not found"):
            parser.parse_file("/non/existent/file.cmmn")

    def test_error_handling_invalid_file_path(self, parser):
        """Test error handling for invalid file paths."""
        with pytest.raises(CMMNParseError):
            parser.parse_file("")

    def test_definition_helper_methods(self, parser, sample_cmmn_file):
        """Test helper methods on CMMNDefinition."""
        definition = parser.parse_file(sample_cmmn_file)

        # Test get_case_by_id
        case = definition.get_case_by_id("Case_1")
        assert case is not None
        assert case.id == "Case_1"

        # Test non-existent case
        non_existent = definition.get_case_by_id("NonExistent")
        assert non_existent is None

        # Test get_all_plan_items
        all_items = definition.get_all_plan_items()
        assert len(all_items) >= 7  # We know there are at least 7 plan items

    def test_empty_elements_handling(self, parser):
        """Test handling of empty optional elements."""
        minimal_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <cmmn:definitions xmlns:cmmn="http://www.omg.org/spec/CMMN/20151109/MODEL">
            <cmmn:case id="EmptyCase">
                <cmmn:casePlanModel id="EmptyPlan">
                    <cmmn:sentry id="EmptySentry"/>
                    <cmmn:planItem id="EmptyPlanItem"/>
                </cmmn:casePlanModel>
            </cmmn:case>
        </cmmn:definitions>"""

        definition = parser.parse_string(minimal_xml)
        case = definition.cases[0]
        plan_model = case.case_plan_model

        # Test empty sentry
        sentry = plan_model.sentries[0]
        assert sentry.id == "EmptySentry"
        assert sentry.name is None
        assert len(sentry.on_parts) == 0
        assert sentry.if_part is None

        # Test empty plan item
        plan_item = plan_model.plan_items[0]
        assert plan_item.id == "EmptyPlanItem"
        assert plan_item.name is None
        assert plan_item.definition_ref is None
        assert len(plan_item.entry_criteria) == 0
        assert plan_item.item_control is None

    def test_multiple_cases_parsing(self, parser):
        """Test parsing multiple cases in one definition."""
        multi_case_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <cmmn:definitions xmlns:cmmn="http://www.omg.org/spec/CMMN/20151109/MODEL"
                           targetNamespace="http://example.com/multi">
            <cmmn:case id="Case1" name="First Case">
                <cmmn:casePlanModel id="Plan1"/>
            </cmmn:case>
            <cmmn:case id="Case2" name="Second Case">
                <cmmn:casePlanModel id="Plan2"/>
            </cmmn:case>
        </cmmn:definitions>"""

        definition = parser.parse_string(multi_case_xml)
        assert len(definition.cases) == 2

        assert definition.cases[0].id == "Case1"
        assert definition.cases[0].name == "First Case"
        assert definition.cases[1].id == "Case2"
        assert definition.cases[1].name == "Second Case"

    def test_namespaces_handling(self, parser):
        """Test proper namespace handling."""
        namespaced_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <definitions xmlns="http://www.omg.org/spec/CMMN/20151109/MODEL"
                     targetNamespace="http://example.com/ns">
            <case id="NSCase">
                <casePlanModel id="NSPlan"/>
            </case>
        </definitions>"""

        # This should work with default namespace
        definition = parser.parse_string(namespaced_xml)
        assert len(definition.cases) == 1
        assert definition.cases[0].id == "NSCase"
