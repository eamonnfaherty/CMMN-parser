from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List, Optional, Union


class CMMNElementType(Enum):
    CASE = "case"
    STAGE = "stage"
    TASK = "task"
    HUMAN_TASK = "humanTask"
    PROCESS_TASK = "processTask"
    CASE_TASK = "caseTask"
    MILESTONE = "milestone"
    EVENT_LISTENER = "eventListener"
    TIMER_EVENT_LISTENER = "timerEventListener"
    USER_EVENT_LISTENER = "userEventListener"
    SENTRY = "sentry"
    CRITERION = "criterion"
    ENTRY_CRITERION = "entryCriterion"
    EXIT_CRITERION = "exitCriterion"
    REACTIVATION_CRITERION = "reactivationCriterion"
    CONNECTOR = "connector"
    ASSOCIATION = "association"
    CASE_FILE_ITEM = "caseFileItem"


class PlanItemLifecycleState(Enum):
    AVAILABLE = "available"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    TERMINATED = "terminated"
    FAILED = "failed"


@dataclass
class CMMNElement:
    id: str
    name: Optional[str] = None
    documentation: Optional[str] = None
    element_type: Optional[CMMNElementType] = None


@dataclass
class PlanItem(CMMNElement):
    definition_ref: Optional[str] = None
    entry_criteria: List[str] = field(default_factory=list)
    exit_criteria: List[str] = field(default_factory=list)
    reactivation_criteria: List[str] = field(default_factory=list)
    item_control: Optional["ItemControl"] = None


@dataclass
class ItemControl:
    required_rule: Optional[str] = None
    repetition_rule: Optional[str] = None
    manual_activation_rule: Optional[str] = None


@dataclass
class Stage(CMMNElement):
    plan_items: List[PlanItem] = field(default_factory=list)
    sentries: List["Sentry"] = field(default_factory=list)
    case_file_items: List["CaseFileItem"] = field(default_factory=list)
    auto_complete: bool = False
    # Dynamic attributes for parser use
    _task_definitions: List[Union["HumanTask", "ProcessTask", "CaseTask"]] = field(
        default_factory=list
    )
    _event_definitions: List[Union["TimerEventListener", "UserEventListener"]] = field(
        default_factory=list
    )
    _milestone_definitions: List["Milestone"] = field(default_factory=list)
    _stage_definitions: List["Stage"] = field(default_factory=list)
    _criteria_definitions: List[Union["EntryCriterion", "ExitCriterion"]] = field(
        default_factory=list
    )

    def __post_init__(self) -> None:
        self.element_type = CMMNElementType.STAGE


@dataclass
class Task(CMMNElement):
    is_blocking: bool = True

    def __post_init__(self) -> None:
        self.element_type = CMMNElementType.TASK


@dataclass
class HumanTask(Task):
    performer: Optional[str] = None

    def __post_init__(self) -> None:
        self.element_type = CMMNElementType.HUMAN_TASK


@dataclass
class ProcessTask(Task):
    process_ref: Optional[str] = None

    def __post_init__(self) -> None:
        self.element_type = CMMNElementType.PROCESS_TASK


@dataclass
class CaseTask(Task):
    case_ref: Optional[str] = None

    def __post_init__(self) -> None:
        self.element_type = CMMNElementType.CASE_TASK


@dataclass
class Milestone(CMMNElement):
    def __post_init__(self) -> None:
        self.element_type = CMMNElementType.MILESTONE


@dataclass
class EventListener(CMMNElement):
    def __post_init__(self) -> None:
        self.element_type = CMMNElementType.EVENT_LISTENER


@dataclass
class TimerEventListener(EventListener):
    timer_expression: Optional[str] = None

    def __post_init__(self) -> None:
        self.element_type = CMMNElementType.TIMER_EVENT_LISTENER


@dataclass
class UserEventListener(EventListener):
    authorized_role_refs: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.element_type = CMMNElementType.USER_EVENT_LISTENER


@dataclass
class Criterion(CMMNElement):
    sentry_ref: Optional[str] = None


@dataclass
class EntryCriterion(Criterion):
    def __post_init__(self) -> None:
        self.element_type = CMMNElementType.ENTRY_CRITERION


@dataclass
class ExitCriterion(Criterion):
    def __post_init__(self) -> None:
        self.element_type = CMMNElementType.EXIT_CRITERION


@dataclass
class ReactivationCriterion(Criterion):
    def __post_init__(self) -> None:
        self.element_type = CMMNElementType.REACTIVATION_CRITERION


@dataclass
class Sentry(CMMNElement):
    on_parts: List["OnPart"] = field(default_factory=list)
    if_part: Optional["IfPart"] = None

    def __post_init__(self) -> None:
        self.element_type = CMMNElementType.SENTRY


@dataclass
class OnPart:
    id: str
    source_ref: Optional[str] = None
    standard_event: Optional[str] = None


@dataclass
class IfPart:
    id: str
    condition: Optional[str] = None


@dataclass
class CaseFileItem(CMMNElement):
    definition_type: Optional[str] = None
    multiplicity: Optional[str] = None
    source_ref: Optional[str] = None
    target_refs: List[str] = field(default_factory=list)
    children: List["CaseFileItem"] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.element_type = CMMNElementType.CASE_FILE_ITEM


@dataclass
class Association(CMMNElement):
    source_ref: str = ""
    target_ref: str = ""
    association_direction: Optional[str] = None

    def __post_init__(self) -> None:
        self.element_type = CMMNElementType.ASSOCIATION


@dataclass
class Case(CMMNElement):
    case_file_model: Optional["CaseFileModel"] = None
    case_plan_model: Optional["CasePlanModel"] = None
    case_roles: List["Role"] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.element_type = CMMNElementType.CASE


@dataclass
class CaseFileModel:
    id: str
    case_file_items: List[CaseFileItem] = field(default_factory=list)


@dataclass
class CasePlanModel(Stage):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.element_type = CMMNElementType.STAGE


@dataclass
class Role:
    id: str
    name: Optional[str] = None


@dataclass
class CMMNDefinition:
    target_namespace: Optional[str] = None
    expression_language: Optional[str] = None
    exporter: Optional[str] = None
    exporter_version: Optional[str] = None
    cases: List[Case] = field(default_factory=list)

    def get_case_by_id(self, case_id: str) -> Optional[Case]:
        return next((case for case in self.cases if case.id == case_id), None)

    def get_all_plan_items(self) -> List[PlanItem]:
        plan_items = []
        for case in self.cases:
            if case.case_plan_model:
                plan_items.extend(self._get_stage_plan_items(case.case_plan_model))
        return plan_items

    def _get_stage_plan_items(self, stage: Stage) -> List[PlanItem]:
        plan_items = stage.plan_items.copy()
        # Note: This is a simple implementation that could be enhanced
        # to recursively search nested stages if needed
        return plan_items
