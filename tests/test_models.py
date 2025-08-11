import pytest
from cmmn_parser.models import (
    Association,
    Case,
    CaseFileItem,
    CaseFileModel,
    CasePlanModel,
    CaseTask,
    CMMNDefinition,
    CMMNElementType,
    EntryCriterion,
    EventListener,
    ExitCriterion,
    HumanTask,
    IfPart,
    ItemControl,
    Milestone,
    OnPart,
    PlanItem,
    PlanItemLifecycleState,
    ProcessTask,
    ReactivationCriterion,
    Role,
    Sentry,
    Stage,
    Task,
    TimerEventListener,
    UserEventListener,
)


class TestModels:

    def test_cmmn_element_type_enum(self):
        """Test CMMNElementType enum values."""
        assert CMMNElementType.CASE.value == "case"
        assert CMMNElementType.STAGE.value == "stage"
        assert CMMNElementType.TASK.value == "task"
        assert CMMNElementType.HUMAN_TASK.value == "humanTask"
        assert CMMNElementType.PROCESS_TASK.value == "processTask"
        assert CMMNElementType.CASE_TASK.value == "caseTask"
        assert CMMNElementType.MILESTONE.value == "milestone"
        assert CMMNElementType.EVENT_LISTENER.value == "eventListener"
        assert CMMNElementType.TIMER_EVENT_LISTENER.value == "timerEventListener"
        assert CMMNElementType.USER_EVENT_LISTENER.value == "userEventListener"

    def test_plan_item_lifecycle_state_enum(self):
        """Test PlanItemLifecycleState enum values."""
        assert PlanItemLifecycleState.AVAILABLE.value == "available"
        assert PlanItemLifecycleState.ENABLED.value == "enabled"
        assert PlanItemLifecycleState.DISABLED.value == "disabled"
        assert PlanItemLifecycleState.ACTIVE.value == "active"
        assert PlanItemLifecycleState.SUSPENDED.value == "suspended"
        assert PlanItemLifecycleState.COMPLETED.value == "completed"
        assert PlanItemLifecycleState.TERMINATED.value == "terminated"
        assert PlanItemLifecycleState.FAILED.value == "failed"

    def test_case_creation_and_element_type(self):
        """Test Case model creation and automatic element type setting."""
        case = Case(id="test_case", name="Test Case")

        assert case.id == "test_case"
        assert case.name == "Test Case"
        assert case.element_type == CMMNElementType.CASE
        assert case.case_file_model is None
        assert case.case_plan_model is None
        assert len(case.case_roles) == 0

    def test_stage_creation_and_defaults(self):
        """Test Stage model with default values."""
        stage = Stage(id="test_stage", name="Test Stage")

        assert stage.id == "test_stage"
        assert stage.name == "Test Stage"
        assert stage.element_type == CMMNElementType.STAGE
        assert len(stage.plan_items) == 0
        assert len(stage.sentries) == 0
        assert len(stage.case_file_items) == 0
        assert stage.auto_complete is False

    def test_stage_with_auto_complete(self):
        """Test Stage with auto_complete set to True."""
        stage = Stage(id="auto_stage", auto_complete=True)

        assert stage.auto_complete is True

    def test_human_task_creation(self):
        """Test HumanTask model creation."""
        task = HumanTask(id="human_task", name="Human Task", performer="user1")

        assert task.id == "human_task"
        assert task.name == "Human Task"
        assert task.element_type == CMMNElementType.HUMAN_TASK
        assert task.performer == "user1"
        assert task.is_blocking is True

    def test_human_task_non_blocking(self):
        """Test HumanTask with non-blocking behavior."""
        task = HumanTask(id="nb_task", is_blocking=False)

        assert task.is_blocking is False

    def test_process_task_creation(self):
        """Test ProcessTask model creation."""
        task = ProcessTask(id="process_task", process_ref="external_process")

        assert task.id == "process_task"
        assert task.element_type == CMMNElementType.PROCESS_TASK
        assert task.process_ref == "external_process"
        assert task.is_blocking is True

    def test_case_task_creation(self):
        """Test CaseTask model creation."""
        task = CaseTask(id="case_task", case_ref="sub_case")

        assert task.id == "case_task"
        assert task.element_type == CMMNElementType.CASE_TASK
        assert task.case_ref == "sub_case"

    def test_milestone_creation(self):
        """Test Milestone model creation."""
        milestone = Milestone(id="milestone1", name="Important Milestone")

        assert milestone.id == "milestone1"
        assert milestone.name == "Important Milestone"
        assert milestone.element_type == CMMNElementType.MILESTONE

    def test_timer_event_listener_creation(self):
        """Test TimerEventListener model creation."""
        timer = TimerEventListener(id="timer1", timer_expression="PT1H")

        assert timer.id == "timer1"
        assert timer.element_type == CMMNElementType.TIMER_EVENT_LISTENER
        assert timer.timer_expression == "PT1H"

    def test_user_event_listener_creation(self):
        """Test UserEventListener model creation."""
        user_event = UserEventListener(
            id="user_event1", authorized_role_refs=["admin", "manager"]
        )

        assert user_event.id == "user_event1"
        assert user_event.element_type == CMMNElementType.USER_EVENT_LISTENER
        assert user_event.authorized_role_refs == ["admin", "manager"]

    def test_user_event_listener_empty_roles(self):
        """Test UserEventListener with empty authorized roles."""
        user_event = UserEventListener(id="user_event2")

        assert len(user_event.authorized_role_refs) == 0

    def test_plan_item_creation(self):
        """Test PlanItem model creation."""
        plan_item = PlanItem(
            id="plan_item1",
            name="Test Plan Item",
            definition_ref="task_def1",
            entry_criteria=["entry1", "entry2"],
            exit_criteria=["exit1"],
        )

        assert plan_item.id == "plan_item1"
        assert plan_item.name == "Test Plan Item"
        assert plan_item.definition_ref == "task_def1"
        assert plan_item.entry_criteria == ["entry1", "entry2"]
        assert plan_item.exit_criteria == ["exit1"]
        assert len(plan_item.reactivation_criteria) == 0
        assert plan_item.item_control is None

    def test_plan_item_with_item_control(self):
        """Test PlanItem with ItemControl."""
        item_control = ItemControl(
            required_rule="required_condition",
            repetition_rule="repetition_condition",
            manual_activation_rule="manual_condition",
        )

        plan_item = PlanItem(id="controlled_item", item_control=item_control)

        assert plan_item.item_control is not None
        assert plan_item.item_control.required_rule == "required_condition"
        assert plan_item.item_control.repetition_rule == "repetition_condition"
        assert plan_item.item_control.manual_activation_rule == "manual_condition"

    def test_item_control_creation(self):
        """Test ItemControl model creation."""
        control = ItemControl(
            required_rule="rule1",
            repetition_rule="rule2",
            manual_activation_rule="rule3",
        )

        assert control.required_rule == "rule1"
        assert control.repetition_rule == "rule2"
        assert control.manual_activation_rule == "rule3"

    def test_item_control_optional_fields(self):
        """Test ItemControl with optional fields as None."""
        control = ItemControl()

        assert control.required_rule is None
        assert control.repetition_rule is None
        assert control.manual_activation_rule is None

    def test_sentry_creation(self):
        """Test Sentry model creation."""
        on_part = OnPart(id="on1", source_ref="source1", standard_event="complete")
        if_part = IfPart(id="if1", condition="condition1")

        sentry = Sentry(
            id="sentry1", name="Test Sentry", on_parts=[on_part], if_part=if_part
        )

        assert sentry.id == "sentry1"
        assert sentry.name == "Test Sentry"
        assert sentry.element_type == CMMNElementType.SENTRY
        assert len(sentry.on_parts) == 1
        assert sentry.if_part is not None

    def test_sentry_empty_parts(self):
        """Test Sentry with empty parts."""
        sentry = Sentry(id="empty_sentry")

        assert len(sentry.on_parts) == 0
        assert sentry.if_part is None

    def test_on_part_creation(self):
        """Test OnPart model creation."""
        on_part = OnPart(
            id="on_part1", source_ref="source_element", standard_event="start"
        )

        assert on_part.id == "on_part1"
        assert on_part.source_ref == "source_element"
        assert on_part.standard_event == "start"

    def test_if_part_creation(self):
        """Test IfPart model creation."""
        if_part = IfPart(id="if_part1", condition="x > 5")

        assert if_part.id == "if_part1"
        assert if_part.condition == "x > 5"

    def test_criterion_models(self):
        """Test different criterion model types."""
        entry = EntryCriterion(id="entry1", sentry_ref="sentry1")
        exit = ExitCriterion(id="exit1", sentry_ref="sentry2")
        reactivation = ReactivationCriterion(id="react1", sentry_ref="sentry3")

        assert entry.element_type == CMMNElementType.ENTRY_CRITERION
        assert exit.element_type == CMMNElementType.EXIT_CRITERION
        assert reactivation.element_type == CMMNElementType.REACTIVATION_CRITERION

        assert entry.sentry_ref == "sentry1"
        assert exit.sentry_ref == "sentry2"
        assert reactivation.sentry_ref == "sentry3"

    def test_case_file_item_creation(self):
        """Test CaseFileItem model creation."""
        child_item = CaseFileItem(id="child1", name="Child Item")

        item = CaseFileItem(
            id="item1",
            name="Parent Item",
            definition_type="DocumentType",
            multiplicity="OneOrMore",
            source_ref="source1",
            target_refs=["target1", "target2"],
            children=[child_item],
        )

        assert item.id == "item1"
        assert item.name == "Parent Item"
        assert item.element_type == CMMNElementType.CASE_FILE_ITEM
        assert item.definition_type == "DocumentType"
        assert item.multiplicity == "OneOrMore"
        assert item.source_ref == "source1"
        assert item.target_refs == ["target1", "target2"]
        assert len(item.children) == 1
        assert item.children[0].id == "child1"

    def test_case_file_item_defaults(self):
        """Test CaseFileItem with default values."""
        item = CaseFileItem(id="simple_item")

        assert item.definition_type is None
        assert item.multiplicity is None
        assert item.source_ref is None
        assert len(item.target_refs) == 0
        assert len(item.children) == 0

    def test_association_creation(self):
        """Test Association model creation."""
        association = Association(
            id="assoc1",
            source_ref="source1",
            target_ref="target1",
            association_direction="unidirectional",
        )

        assert association.id == "assoc1"
        assert association.element_type == CMMNElementType.ASSOCIATION
        assert association.source_ref == "source1"
        assert association.target_ref == "target1"
        assert association.association_direction == "unidirectional"

    def test_role_creation(self):
        """Test Role model creation."""
        role = Role(id="role1", name="Administrator")

        assert role.id == "role1"
        assert role.name == "Administrator"

    def test_role_without_name(self):
        """Test Role creation without name."""
        role = Role(id="role2")

        assert role.id == "role2"
        assert role.name is None

    def test_case_file_model_creation(self):
        """Test CaseFileModel creation."""
        item1 = CaseFileItem(id="item1")
        item2 = CaseFileItem(id="item2")

        model = CaseFileModel(id="file_model1", case_file_items=[item1, item2])

        assert model.id == "file_model1"
        assert len(model.case_file_items) == 2

    def test_case_plan_model_creation(self):
        """Test CasePlanModel creation (inherits from Stage)."""
        plan_item = PlanItem(id="item1")

        plan_model = CasePlanModel(
            id="plan_model1", name="Main Plan", plan_items=[plan_item]
        )

        assert plan_model.id == "plan_model1"
        assert plan_model.name == "Main Plan"
        assert plan_model.element_type == CMMNElementType.STAGE
        assert len(plan_model.plan_items) == 1

    def test_cmmn_definition_creation(self):
        """Test CMMNDefinition creation."""
        case1 = Case(id="case1")
        case2 = Case(id="case2")

        definition = CMMNDefinition(
            target_namespace="http://example.com",
            expression_language="XPath",
            exporter="TestTool",
            exporter_version="1.0",
            cases=[case1, case2],
        )

        assert definition.target_namespace == "http://example.com"
        assert definition.expression_language == "XPath"
        assert definition.exporter == "TestTool"
        assert definition.exporter_version == "1.0"
        assert len(definition.cases) == 2

    def test_cmmn_definition_helper_methods(self):
        """Test CMMNDefinition helper methods."""
        case1 = Case(id="case1", name="First Case")
        case2 = Case(id="case2", name="Second Case")

        # Create case plan model with plan items
        plan_item1 = PlanItem(id="item1")
        plan_item2 = PlanItem(id="item2")
        plan_model = CasePlanModel(id="plan1", plan_items=[plan_item1, plan_item2])
        case1.case_plan_model = plan_model

        definition = CMMNDefinition(cases=[case1, case2])

        # Test get_case_by_id
        found_case = definition.get_case_by_id("case1")
        assert found_case is not None
        assert found_case.name == "First Case"

        not_found = definition.get_case_by_id("case3")
        assert not_found is None

        # Test get_all_plan_items
        all_items = definition.get_all_plan_items()
        assert len(all_items) == 2
        assert all_items[0].id == "item1"
        assert all_items[1].id == "item2"

    def test_cmmn_definition_empty_cases(self):
        """Test CMMNDefinition with empty cases."""
        definition = CMMNDefinition()

        assert len(definition.cases) == 0
        assert definition.get_case_by_id("any") is None
        assert len(definition.get_all_plan_items()) == 0

    def test_model_documentation_field(self):
        """Test documentation field in base CMMNElement."""
        stage = Stage(
            id="documented_stage",
            name="Test Stage",
            documentation="This is a test stage for demonstration purposes.",
        )

        assert stage.documentation == "This is a test stage for demonstration purposes."

    def test_model_optional_fields_none(self):
        """Test that optional fields default to None appropriately."""
        task = Task(id="basic_task")

        assert task.name is None
        assert task.documentation is None
        assert task.element_type == CMMNElementType.TASK
        assert task.is_blocking is True
