"""CMMN Data Models

Data models representing CMMN elements based on the CMMN 1.1 specification.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CMMNElement:
    """Base class for all CMMN elements."""

    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None


@dataclass
class Import(CMMNElement):
    """Represents a CMMN import element."""

    namespace: Optional[str] = None
    location: Optional[str] = None
    import_type: Optional[str] = None


@dataclass
class CaseFileItemDefinition(CMMNElement):
    """Represents a case file item definition."""

    structure_ref: Optional[str] = None
    definitive_property: List[str] = field(default_factory=list)


@dataclass
class PlanItem(CMMNElement):
    """Represents a plan item in a case."""

    definition_ref: Optional[str] = None
    entry_criteria: List[str] = field(default_factory=list)
    exit_criteria: List[str] = field(default_factory=list)


@dataclass
class Milestone(CMMNElement):
    """Represents a milestone."""

    pass


@dataclass
class Task(CMMNElement):
    """Represents a task."""

    is_blocking: bool = True
    task_type: Optional[str] = None


@dataclass
class HumanTask(Task):
    """Represents a human task."""

    performer: Optional[str] = None
    form_key: Optional[str] = None


@dataclass
class ProcessTask(Task):
    """Represents a process task."""

    process_ref: Optional[str] = None


@dataclass
class CaseTask(Task):
    """Represents a case task."""

    case_ref: Optional[str] = None


@dataclass
class DecisionTask(Task):
    """Represents a decision task."""

    decision_ref: Optional[str] = None


@dataclass
class Stage(CMMNElement):
    """Represents a stage."""

    auto_complete: bool = False
    plan_items: List[PlanItem] = field(default_factory=list)


@dataclass
class Sentry(CMMNElement):
    """Represents a sentry."""

    on_part: List[str] = field(default_factory=list)
    if_part: Optional[str] = None


@dataclass
class CasePlanModel(CMMNElement):
    """Represents a case plan model."""

    auto_complete: bool = False
    plan_items: List[PlanItem] = field(default_factory=list)
    sentries: List[Sentry] = field(default_factory=list)
    stages: List[Stage] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)
    milestones: List[Milestone] = field(default_factory=list)


@dataclass
class CaseFileModel(CMMNElement):
    """Represents a case file model."""

    case_file_items: List[str] = field(default_factory=list)


@dataclass
class Case(CMMNElement):
    """Represents a CMMN case."""

    case_plan_model: Optional[CasePlanModel] = None
    case_file_model: Optional[CaseFileModel] = None


@dataclass
class Process(CMMNElement):
    """Represents a process definition."""

    is_executable: bool = True
    implementation_type: Optional[str] = None


@dataclass
class Decision(CMMNElement):
    """Represents a decision definition."""

    decision_logic: Optional[str] = None


@dataclass
class ExtensionElements:
    """Represents extension elements."""

    elements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CMMNDefinitions:
    """Root element representing CMMN definitions."""

    id: Optional[str] = None
    name: Optional[str] = None
    target_namespace: Optional[str] = None
    expression_language: Optional[str] = None
    exporter: Optional[str] = None
    exporter_version: Optional[str] = None
    author: Optional[str] = None
    creation_date: Optional[str] = None

    imports: List[Import] = field(default_factory=list)
    case_file_item_definitions: List[CaseFileItemDefinition] = field(
        default_factory=list
    )
    cases: List[Case] = field(default_factory=list)
    processes: List[Process] = field(default_factory=list)
    decisions: List[Decision] = field(default_factory=list)
    extension_elements: Optional[ExtensionElements] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the definitions to a dictionary representation."""
        result: Dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "targetNamespace": self.target_namespace,
            "expressionLanguage": self.expression_language,
            "exporter": self.exporter,
            "exporterVersion": self.exporter_version,
            "author": self.author,
            "creationDate": self.creation_date,
            "imports": [self._import_to_dict(imp) for imp in self.imports],
            "caseFileItemDefinitions": [
                self._case_file_item_def_to_dict(cfid)
                for cfid in self.case_file_item_definitions
            ],
            "cases": [self._case_to_dict(case) for case in self.cases],
            "processes": [self._process_to_dict(proc) for proc in self.processes],
            "decisions": [self._decision_to_dict(dec) for dec in self.decisions],
        }

        if self.extension_elements:
            result["extensionElements"] = self.extension_elements.elements

        return result

    def _import_to_dict(self, imp: Import) -> Dict[str, Any]:
        """Convert Import to dictionary."""
        return {
            "id": imp.id,
            "namespace": imp.namespace,
            "location": imp.location,
            "importType": imp.import_type,
        }

    def _case_file_item_def_to_dict(
        self, cfid: CaseFileItemDefinition
    ) -> Dict[str, Any]:
        """Convert CaseFileItemDefinition to dictionary."""
        return {
            "id": cfid.id,
            "name": cfid.name,
            "description": cfid.description,
            "structureRef": cfid.structure_ref,
            "definitiveProperty": cfid.definitive_property,
        }

    def _case_to_dict(self, case: Case) -> Dict[str, Any]:
        """Convert Case to dictionary."""
        result: Dict[str, Any] = {
            "id": case.id,
            "name": case.name,
            "description": case.description,
        }

        if case.case_plan_model:
            result["casePlanModel"] = self._case_plan_model_to_dict(
                case.case_plan_model
            )

        if case.case_file_model:
            result["caseFileModel"] = {
                "id": case.case_file_model.id,
                "name": case.case_file_model.name,
                "caseFileItems": case.case_file_model.case_file_items,
            }

        return result

    def _case_plan_model_to_dict(self, cpm: CasePlanModel) -> Dict[str, Any]:
        """Convert CasePlanModel to dictionary."""
        return {
            "id": cpm.id,
            "name": cpm.name,
            "autoComplete": cpm.auto_complete,
            "planItems": [self._plan_item_to_dict(pi) for pi in cpm.plan_items],
            "sentries": [self._sentry_to_dict(s) for s in cpm.sentries],
            "stages": [self._stage_to_dict(s) for s in cpm.stages],
            "tasks": [self._task_to_dict(t) for t in cpm.tasks],
            "milestones": [self._milestone_to_dict(m) for m in cpm.milestones],
        }

    def _plan_item_to_dict(self, pi: PlanItem) -> Dict[str, Any]:
        """Convert PlanItem to dictionary."""
        return {
            "id": pi.id,
            "name": pi.name,
            "definitionRef": pi.definition_ref,
            "entryCriteria": pi.entry_criteria,
            "exitCriteria": pi.exit_criteria,
        }

    def _sentry_to_dict(self, sentry: Sentry) -> Dict[str, Any]:
        """Convert Sentry to dictionary."""
        return {
            "id": sentry.id,
            "name": sentry.name,
            "onPart": sentry.on_part,
            "ifPart": sentry.if_part,
        }

    def _stage_to_dict(self, stage: Stage) -> Dict[str, Any]:
        """Convert Stage to dictionary."""
        return {
            "id": stage.id,
            "name": stage.name,
            "autoComplete": stage.auto_complete,
            "planItems": [self._plan_item_to_dict(pi) for pi in stage.plan_items],
        }

    def _task_to_dict(self, task: Task) -> Dict[str, Any]:
        """Convert Task to dictionary."""
        result = {
            "id": task.id,
            "name": task.name,
            "isBlocking": task.is_blocking,
            "taskType": task.task_type,
        }

        if isinstance(task, HumanTask):
            result.update(
                {
                    "type": "humanTask",
                    "performer": task.performer,
                    "formKey": task.form_key,
                }
            )
        elif isinstance(task, ProcessTask):
            result.update(
                {
                    "type": "processTask",
                    "processRef": task.process_ref,
                }
            )
        elif isinstance(task, CaseTask):
            result.update(
                {
                    "type": "caseTask",
                    "caseRef": task.case_ref,
                }
            )
        elif isinstance(task, DecisionTask):
            result.update(
                {
                    "type": "decisionTask",
                    "decisionRef": task.decision_ref,
                }
            )

        return result

    def _milestone_to_dict(self, milestone: Milestone) -> Dict[str, Any]:
        """Convert Milestone to dictionary."""
        return {
            "id": milestone.id,
            "name": milestone.name,
            "description": milestone.description,
        }

    def _process_to_dict(self, process: Process) -> Dict[str, Any]:
        """Convert Process to dictionary."""
        return {
            "id": process.id,
            "name": process.name,
            "description": process.description,
            "isExecutable": process.is_executable,
            "implementationType": process.implementation_type,
        }

    def _decision_to_dict(self, decision: Decision) -> Dict[str, Any]:
        """Convert Decision to dictionary."""
        return {
            "id": decision.id,
            "name": decision.name,
            "description": decision.description,
            "decisionLogic": decision.decision_logic,
        }
