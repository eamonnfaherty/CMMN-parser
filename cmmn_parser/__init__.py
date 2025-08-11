from pathlib import Path
from typing import Any, Dict, Union

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
from .validation import (
    get_schema_info,
    get_validation_errors,
    validate_cmmn_json,
    validate_cmmn_json_file,
)

__version__ = "0.1.0"
__all__ = [
    # Core classes and parsing
    "CMMNParser",
    "CMMNParseError",
    "CMMNDefinition",
    # Validation functions
    "validate_cmmn_json",
    "validate_cmmn_json_file",
    "get_validation_errors",
    "get_schema_info",
    # Convenience functions
    "parse_cmmn_file",
    "parse_cmmn_string",
    "parse_cmmn_json",
    "parse_cmmn_json_file",
    # Model classes
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
    """Convenience function to parse a CMMN file (XML or JSON)."""
    parser = CMMNParser()
    return parser.parse_file(file_path)


def parse_cmmn_string(cmmn_text: str) -> CMMNDefinition:
    """Convenience function to parse CMMN text (XML or JSON auto-detected)."""
    parser = CMMNParser()
    return parser.parse_string(cmmn_text)


def parse_cmmn_json(cmmn_json: Union[str, Dict[str, Any]]) -> CMMNDefinition:
    """Convenience function to parse CMMN JSON data."""
    parser = CMMNParser()
    if isinstance(cmmn_json, dict):
        import json

        cmmn_json = json.dumps(cmmn_json)
    return parser.parse_json_string(cmmn_json)


def parse_cmmn_json_file(file_path: Union[str, Path]) -> CMMNDefinition:
    """Convenience function to parse a CMMN JSON file."""
    parser = CMMNParser()
    return parser.parse_json_file(file_path)
