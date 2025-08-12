"""Tests for CMMN data models."""

import pytest

from cmmn_parser.models import (
    Case,
    CaseFileItemDefinition,
    CasePlanModel,
    CaseTask,
    CMMNDefinitions,
    Decision,
    DecisionTask,
    ExtensionElements,
    HumanTask,
    Import,
    Milestone,
    PlanItem,
    Process,
    ProcessTask,
    Sentry,
    Stage,
    Task,
)


class TestCMMNElement:
    """Test base CMMN element functionality."""

    def test_task_creation(self):
        """Test basic task creation."""
        task = Task(id="task1", name="Test Task")
        assert task.id == "task1"
        assert task.name == "Test Task"
        assert task.is_blocking is True
        assert task.task_type is None


class TestTaskTypes:
    """Test different task types."""

    def test_human_task(self):
        """Test human task creation."""
        task = HumanTask(
            id="human1", name="Human Task", performer="user1", form_key="form1"
        )
        assert task.id == "human1"
        assert task.name == "Human Task"
        assert task.performer == "user1"
        assert task.form_key == "form1"
        assert task.is_blocking is True

    def test_process_task(self):
        """Test process task creation."""
        task = ProcessTask(
            id="process1", name="Process Task", process_ref="process_def_1"
        )
        assert task.id == "process1"
        assert task.name == "Process Task"
        assert task.process_ref == "process_def_1"

    def test_case_task(self):
        """Test case task creation."""
        task = CaseTask(id="case1", name="Case Task", case_ref="case_def_1")
        assert task.id == "case1"
        assert task.name == "Case Task"
        assert task.case_ref == "case_def_1"

    def test_decision_task(self):
        """Test decision task creation."""
        task = DecisionTask(
            id="decision1", name="Decision Task", decision_ref="decision_def_1"
        )
        assert task.id == "decision1"
        assert task.name == "Decision Task"
        assert task.decision_ref == "decision_def_1"


class TestStage:
    """Test stage functionality."""

    def test_stage_creation(self):
        """Test basic stage creation."""
        stage = Stage(id="stage1", name="Test Stage")
        assert stage.id == "stage1"
        assert stage.name == "Test Stage"
        assert stage.auto_complete is False
        assert len(stage.plan_items) == 0

    def test_stage_with_plan_items(self):
        """Test stage with plan items."""
        plan_item = PlanItem(id="pi1", name="Plan Item 1")
        stage = Stage(id="stage1", name="Test Stage", plan_items=[plan_item])
        assert len(stage.plan_items) == 1
        assert stage.plan_items[0].id == "pi1"


class TestMilestone:
    """Test milestone functionality."""

    def test_milestone_creation(self):
        """Test basic milestone creation."""
        milestone = Milestone(id="milestone1", name="Test Milestone")
        assert milestone.id == "milestone1"
        assert milestone.name == "Test Milestone"


class TestSentry:
    """Test sentry functionality."""

    def test_sentry_creation(self):
        """Test basic sentry creation."""
        sentry = Sentry(id="sentry1", name="Test Sentry")
        assert sentry.id == "sentry1"
        assert sentry.name == "Test Sentry"
        assert len(sentry.on_part) == 0
        assert sentry.if_part is None

    def test_sentry_with_conditions(self):
        """Test sentry with conditions."""
        sentry = Sentry(
            id="sentry1",
            name="Test Sentry",
            on_part=["task1", "task2"],
            if_part="condition",
        )
        assert len(sentry.on_part) == 2
        assert sentry.if_part == "condition"


class TestPlanItem:
    """Test plan item functionality."""

    def test_plan_item_creation(self):
        """Test basic plan item creation."""
        plan_item = PlanItem(id="pi1", name="Plan Item 1")
        assert plan_item.id == "pi1"
        assert plan_item.name == "Plan Item 1"
        assert plan_item.definition_ref is None
        assert len(plan_item.entry_criteria) == 0
        assert len(plan_item.exit_criteria) == 0

    def test_plan_item_with_criteria(self):
        """Test plan item with criteria."""
        plan_item = PlanItem(
            id="pi1",
            name="Plan Item 1",
            definition_ref="task1",
            entry_criteria=["sentry1"],
            exit_criteria=["sentry2"],
        )
        assert plan_item.definition_ref == "task1"
        assert len(plan_item.entry_criteria) == 1
        assert len(plan_item.exit_criteria) == 1


class TestCasePlanModel:
    """Test case plan model functionality."""

    def test_case_plan_model_creation(self):
        """Test basic case plan model creation."""
        cpm = CasePlanModel(id="cpm1", name="Case Plan Model")
        assert cpm.id == "cpm1"
        assert cpm.name == "Case Plan Model"
        assert cpm.auto_complete is False
        assert len(cpm.plan_items) == 0
        assert len(cpm.sentries) == 0
        assert len(cpm.stages) == 0
        assert len(cpm.tasks) == 0
        assert len(cpm.milestones) == 0

    def test_case_plan_model_with_elements(self):
        """Test case plan model with various elements."""
        plan_item = PlanItem(id="pi1", name="Plan Item 1")
        task = Task(id="task1", name="Task 1")
        milestone = Milestone(id="milestone1", name="Milestone 1")

        cpm = CasePlanModel(
            id="cpm1",
            name="Case Plan Model",
            plan_items=[plan_item],
            tasks=[task],
            milestones=[milestone],
        )

        assert len(cpm.plan_items) == 1
        assert len(cpm.tasks) == 1
        assert len(cpm.milestones) == 1


class TestCase:
    """Test case functionality."""

    def test_case_creation(self):
        """Test basic case creation."""
        case = Case(id="case1", name="Test Case")
        assert case.id == "case1"
        assert case.name == "Test Case"
        assert case.case_plan_model is None
        assert case.case_file_model is None

    def test_case_with_plan_model(self):
        """Test case with case plan model."""
        cpm = CasePlanModel(id="cpm1", name="Case Plan Model")
        case = Case(id="case1", name="Test Case", case_plan_model=cpm)
        assert case.case_plan_model is not None
        assert case.case_plan_model.id == "cpm1"


class TestImport:
    """Test import functionality."""

    def test_import_creation(self):
        """Test basic import creation."""
        imp = Import(
            id="import1",
            namespace="http://example.com",
            location="example.xsd",
            import_type="http://example.com/type",
        )
        assert imp.id == "import1"
        assert imp.namespace == "http://example.com"
        assert imp.location == "example.xsd"
        assert imp.import_type == "http://example.com/type"


class TestCaseFileItemDefinition:
    """Test case file item definition functionality."""

    def test_case_file_item_definition_creation(self):
        """Test basic case file item definition creation."""
        cfid = CaseFileItemDefinition(
            id="cfid1", name="Case File Item", structure_ref="structure1"
        )
        assert cfid.id == "cfid1"
        assert cfid.name == "Case File Item"
        assert cfid.structure_ref == "structure1"
        assert len(cfid.definitive_property) == 0

    def test_case_file_item_definition_with_properties(self):
        """Test case file item definition with properties."""
        cfid = CaseFileItemDefinition(
            id="cfid1", name="Case File Item", definitive_property=["prop1", "prop2"]
        )
        assert len(cfid.definitive_property) == 2
        assert "prop1" in cfid.definitive_property
        assert "prop2" in cfid.definitive_property


class TestProcess:
    """Test process functionality."""

    def test_process_creation(self):
        """Test basic process creation."""
        process = Process(id="process1", name="Test Process")
        assert process.id == "process1"
        assert process.name == "Test Process"
        assert process.is_executable is True
        assert process.implementation_type is None


class TestDecision:
    """Test decision functionality."""

    def test_decision_creation(self):
        """Test basic decision creation."""
        decision = Decision(id="decision1", name="Test Decision")
        assert decision.id == "decision1"
        assert decision.name == "Test Decision"
        assert decision.decision_logic is None

    def test_decision_with_logic(self):
        """Test decision with logic."""
        decision = Decision(
            id="decision1", name="Test Decision", decision_logic="some logic"
        )
        assert decision.decision_logic == "some logic"


class TestExtensionElements:
    """Test extension elements functionality."""

    def test_extension_elements_creation(self):
        """Test basic extension elements creation."""
        ext = ExtensionElements()
        assert len(ext.elements) == 0

    def test_extension_elements_with_data(self):
        """Test extension elements with data."""
        data = {"custom": {"value": "test"}}
        ext = ExtensionElements(elements=data)
        assert ext.elements["custom"]["value"] == "test"


class TestCMMNDefinitions:
    """Test CMMN definitions functionality."""

    def test_definitions_creation(self):
        """Test basic definitions creation."""
        definitions = CMMNDefinitions(id="def1", name="Test Definitions")
        assert definitions.id == "def1"
        assert definitions.name == "Test Definitions"
        assert len(definitions.imports) == 0
        assert len(definitions.cases) == 0
        assert len(definitions.processes) == 0
        assert len(definitions.decisions) == 0

    def test_definitions_with_elements(self):
        """Test definitions with various elements."""
        imp = Import(id="import1", namespace="http://example.com")
        case = Case(id="case1", name="Test Case")
        process = Process(id="process1", name="Test Process")
        decision = Decision(id="decision1", name="Test Decision")

        definitions = CMMNDefinitions(
            id="def1",
            name="Test Definitions",
            imports=[imp],
            cases=[case],
            processes=[process],
            decisions=[decision],
        )

        assert len(definitions.imports) == 1
        assert len(definitions.cases) == 1
        assert len(definitions.processes) == 1
        assert len(definitions.decisions) == 1

    def test_definitions_to_dict(self):
        """Test converting definitions to dictionary."""
        definitions = CMMNDefinitions(
            id="def1", name="Test Definitions", target_namespace="http://example.com"
        )

        data = definitions.to_dict()
        assert data["id"] == "def1"
        assert data["name"] == "Test Definitions"
        assert data["targetNamespace"] == "http://example.com"
        assert isinstance(data["imports"], list)
        assert isinstance(data["cases"], list)

    def test_definitions_to_dict_with_case(self):
        """Test converting definitions with case to dictionary."""
        task = HumanTask(id="task1", name="Human Task", performer="user1")
        cpm = CasePlanModel(id="cpm1", name="Case Plan", tasks=[task])
        case = Case(id="case1", name="Test Case", case_plan_model=cpm)

        definitions = CMMNDefinitions(id="def1", name="Test Definitions", cases=[case])

        data = definitions.to_dict()
        assert len(data["cases"]) == 1
        assert data["cases"][0]["id"] == "case1"
        assert data["cases"][0]["casePlanModel"]["id"] == "cpm1"
        assert len(data["cases"][0]["casePlanModel"]["tasks"]) == 1
        assert data["cases"][0]["casePlanModel"]["tasks"][0]["type"] == "humanTask"
