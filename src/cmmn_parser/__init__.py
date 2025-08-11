from .parser import CMMNParser, CMMNParseError
from .models import (
    CMMNDefinition,
    Case,
    CasePlanModel,
    CaseFileModel,
    CaseFileItem,
    Stage,
    Task,
    HumanTask,
    ProcessTask,
    CaseTask,
    Milestone,
    EventListener,
    TimerEventListener,
    UserEventListener,
    Sentry,
    OnPart,
    IfPart,
    EntryCriterion,
    ExitCriterion,
    ReactivationCriterion,
    PlanItem,
    ItemControl,
    Association,
    Role,
    CMMNElementType,
    PlanItemLifecycleState,
)

__version__ = "0.1.0"
__all__ = [
    "CMMNParser",
    "CMMNParseError",
    "CMMNDefinition",
    "Case",
    "CasePlanModel",
    "CaseFileModel",
    "CaseFileItem",
    "Stage",
    "Task",
    "HumanTask",
    "ProcessTask",
    "CaseTask",
    "Milestone",
    "EventListener",
    "TimerEventListener",
    "UserEventListener",
    "Sentry",
    "OnPart",
    "IfPart",
    "EntryCriterion",
    "ExitCriterion",
    "ReactivationCriterion",
    "PlanItem",
    "ItemControl",
    "Association",
    "Role",
    "CMMNElementType",
    "PlanItemLifecycleState",
]


def parse_cmmn_file(file_path):
    """Convenience function to parse a CMMN file."""
    parser = CMMNParser()
    return parser.parse_file(file_path)


def parse_cmmn_string(cmmn_text):
    """Convenience function to parse CMMN text."""
    parser = CMMNParser()
    return parser.parse_string(cmmn_text)
