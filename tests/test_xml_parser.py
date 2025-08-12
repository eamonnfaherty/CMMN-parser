"""Tests for CMMN XML parser functionality."""

import pytest
from lxml import etree

from cmmn_parser.exceptions import CMMNParsingError
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
from cmmn_parser.xml_parser import XMLParser


class TestXMLParser:
    """Test XML parser functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = XMLParser()

    def test_parser_initialization(self):
        """Test parser initialization."""
        parser = XMLParser()
        assert parser.CMMN_NAMESPACE == "http://www.omg.org/spec/CMMN/20151109/MODEL"
        assert "cmmn" in parser.namespaces

    def test_parse_invalid_xml_syntax(self):
        """Test parsing XML with invalid syntax."""
        invalid_xml = "<invalid><unclosed>"
        with pytest.raises(CMMNParsingError, match="Invalid XML syntax"):
            self.parser.parse(invalid_xml)

    def test_parse_wrong_root_element(self):
        """Test parsing XML with wrong root element."""
        wrong_root = '<?xml version="1.0"?><wrong/>'
        with pytest.raises(
            CMMNParsingError, match="Root element must be 'definitions'"
        ):
            self.parser.parse(wrong_root)

    def test_parse_basic_definitions(self):
        """Test parsing basic definitions element."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/CMMN/20151109/MODEL"
             id="def1" name="Test Definitions" 
             targetNamespace="http://example.com"
             exporter="test" exporterVersion="1.0"
             author="test author" creationDate="2023-01-01">
</definitions>"""

        result = self.parser.parse(xml)
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
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/CMMN/20151109/MODEL">
    <import id="import1" namespace="http://example.com" 
            location="example.xsd" importType="http://example.com/type"/>
</definitions>"""

        result = self.parser.parse(xml)
        assert len(result.imports) == 1
        import_obj = result.imports[0]
        assert import_obj.id == "import1"
        assert import_obj.namespace == "http://example.com"
        assert import_obj.location == "example.xsd"
        assert import_obj.import_type == "http://example.com/type"

    def test_parse_case_file_item_definition(self):
        """Test parsing case file item definition."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/CMMN/20151109/MODEL">
    <caseFileItemDefinition id="cfid1" name="Test Item" structureRef="struct1">
        <definitiveProperty name="prop1"/>
        <definitiveProperty name="prop2"/>
    </caseFileItemDefinition>
</definitions>"""

        result = self.parser.parse(xml)
        assert len(result.case_file_item_definitions) == 1
        cfid = result.case_file_item_definitions[0]
        assert cfid.id == "cfid1"
        assert cfid.name == "Test Item"
        assert cfid.structure_ref == "struct1"
        assert len(cfid.definitive_property) == 2
        assert "prop1" in cfid.definitive_property
        assert "prop2" in cfid.definitive_property

    def test_parse_basic_case(self):
        """Test parsing basic case element."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/CMMN/20151109/MODEL">
    <case id="case1" name="Test Case">
    </case>
</definitions>"""

        result = self.parser.parse(xml)
        assert len(result.cases) == 1
        case = result.cases[0]
        assert case.id == "case1"
        assert case.name == "Test Case"
        assert case.case_plan_model is None

    def test_parse_case_with_plan_model(self):
        """Test parsing case with case plan model."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/CMMN/20151109/MODEL">
    <case id="case1" name="Test Case">
        <casePlanModel id="cpm1" name="Case Plan Model" autoComplete="true">
        </casePlanModel>
    </case>
</definitions>"""

        result = self.parser.parse(xml)
        case = result.cases[0]
        assert case.case_plan_model is not None
        cpm = case.case_plan_model
        assert cpm.id == "cpm1"
        assert cpm.name == "Case Plan Model"
        assert cpm.auto_complete is True

    def test_parse_task_elements(self):
        """Test parsing different task elements."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/CMMN/20151109/MODEL">
    <case id="case1" name="Test Case">
        <casePlanModel id="cpm1" name="Case Plan Model">
            <task id="task1" name="Basic Task" isBlocking="false"/>
            <humanTask id="task2" name="Human Task" performer="user1" formKey="form1"/>
            <processTask id="task3" name="Process Task" processRef="process1"/>
            <caseTask id="task4" name="Case Task" caseRef="case1"/>
            <decisionTask id="task5" name="Decision Task" decisionRef="decision1"/>
        </casePlanModel>
    </case>
</definitions>"""

        result = self.parser.parse(xml)
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
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/CMMN/20151109/MODEL">
    <case id="case1" name="Test Case">
        <casePlanModel id="cpm1" name="Case Plan Model">
            <milestone id="milestone1" name="Test Milestone"/>
        </casePlanModel>
    </case>
</definitions>"""

        result = self.parser.parse(xml)
        cpm = result.cases[0].case_plan_model
        assert len(cpm.milestones) == 1
        milestone = cpm.milestones[0]
        assert milestone.id == "milestone1"
        assert milestone.name == "Test Milestone"

    def test_parse_stage(self):
        """Test parsing stage element."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/CMMN/20151109/MODEL">
    <case id="case1" name="Test Case">
        <casePlanModel id="cpm1" name="Case Plan Model">
            <stage id="stage1" name="Test Stage" autoComplete="true">
                <planItem id="pi1" name="Plan Item 1" definitionRef="task1"/>
            </stage>
        </casePlanModel>
    </case>
</definitions>"""

        result = self.parser.parse(xml)
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
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/CMMN/20151109/MODEL">
    <case id="case1" name="Test Case">
        <casePlanModel id="cpm1" name="Case Plan Model">
            <planItem id="pi1" name="Plan Item 1" definitionRef="task1">
                <entryCriterion sentryRef="sentry1"/>
                <exitCriterion sentryRef="sentry2"/>
            </planItem>
        </casePlanModel>
    </case>
</definitions>"""

        result = self.parser.parse(xml)
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
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/CMMN/20151109/MODEL">
    <case id="case1" name="Test Case">
        <casePlanModel id="cpm1" name="Case Plan Model">
            <sentry id="sentry1" name="Test Sentry">
                <planItemOnPart sourceRef="task1"/>
                <planItemOnPart sourceRef="task2"/>
                <ifPart>condition expression</ifPart>
            </sentry>
        </casePlanModel>
    </case>
</definitions>"""

        result = self.parser.parse(xml)
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
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/CMMN/20151109/MODEL">
    <process id="process1" name="Test Process" isExecutable="false" 
             implementationType="custom"/>
</definitions>"""

        result = self.parser.parse(xml)
        assert len(result.processes) == 1
        process = result.processes[0]
        assert process.id == "process1"
        assert process.name == "Test Process"
        assert process.is_executable is False
        assert process.implementation_type == "custom"

    def test_parse_decision(self):
        """Test parsing decision element."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/CMMN/20151109/MODEL">
    <decision id="decision1" name="Test Decision">
        <decisionLogic>decision logic content</decisionLogic>
    </decision>
</definitions>"""

        result = self.parser.parse(xml)
        assert len(result.decisions) == 1
        decision = result.decisions[0]
        assert decision.id == "decision1"
        assert decision.name == "Test Decision"
        assert decision.decision_logic == "decision logic content"

    def test_parse_extension_elements(self):
        """Test parsing extension elements."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/CMMN/20151109/MODEL">
    <extensionElements>
        <custom attr="value">content</custom>
        <another>
            <nested attr="nested">nested content</nested>
        </another>
    </extensionElements>
</definitions>"""

        result = self.parser.parse(xml)
        assert result.extension_elements is not None
        elements = result.extension_elements.elements
        assert "custom" in elements
        assert elements["custom"]["attr"] == "value"
        assert elements["custom"]["text"] == "content"
        assert "another" in elements

    def test_strip_namespace(self):
        """Test namespace stripping utility."""
        tag_with_ns = "{http://www.omg.org/spec/CMMN/20151109/MODEL}definitions"
        result = self.parser._strip_namespace(tag_with_ns)
        assert result == "definitions"

        tag_without_ns = "definitions"
        result2 = self.parser._strip_namespace(tag_without_ns)
        assert result2 == "definitions"

    def test_element_to_dict(self):
        """Test element to dictionary conversion."""
        xml_content = '<test attr="value">text content<child attr2="value2">child text</child></test>'
        element = etree.fromstring(xml_content)

        result = self.parser._element_to_dict(element)
        assert result["attr"] == "value"
        assert result["text"] == "text content"
        assert "children" in result
        assert "child" in result["children"]
        assert len(result["children"]["child"]) == 1
        assert result["children"]["child"][0]["attr2"] == "value2"
        assert result["children"]["child"][0]["text"] == "child text"
