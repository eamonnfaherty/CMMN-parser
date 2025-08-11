from pathlib import Path
from typing import Union

from .models import (
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
from .parser import CMMNParseError, CMMNParser

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


def parse_cmmn_file(file_path: Union[str, Path]) -> CMMNDefinition:
    """Convenience function to parse a CMMN file."""
    parser = CMMNParser()
    return parser.parse_file(file_path)


def parse_cmmn_string(cmmn_text: str) -> CMMNDefinition:
    """Convenience function to parse CMMN text."""
    parser = CMMNParser()
    return parser.parse_string(cmmn_text)
