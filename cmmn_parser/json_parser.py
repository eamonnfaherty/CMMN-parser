"""CMMN JSON Parser

Handles parsing of CMMN JSON format.
"""

from typing import Any, Dict

from .exceptions import CMMNParsingError
from .models import (
    Case,
    CaseFileItemDefinition,
    CaseFileModel,
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


class JSONParser:
    """Parser for CMMN JSON format."""

    def parse(self, data: Dict[str, Any]) -> CMMNDefinitions:
        """Parse CMMN JSON data.

        Args:
            data: The JSON data as a dictionary

        Returns:
            CMMNDefinitions: Parsed CMMN definitions

        Raises:
            CMMNParsingError: If parsing fails
        """
        if not isinstance(data, dict):
            raise CMMNParsingError("JSON data must be a dictionary")

        return self._parse_definitions(data)

    def _parse_definitions(self, data: Dict[str, Any]) -> CMMNDefinitions:
        """Parse the definitions from JSON data.

        Args:
            data: The definitions JSON data

        Returns:
            CMMNDefinitions: Parsed definitions
        """
        definitions = self._create_base_definitions(data)
        self._populate_definitions_collections(definitions, data)
        return definitions

    def _create_base_definitions(self, data: Dict[str, Any]) -> CMMNDefinitions:
        """Create base definitions with metadata."""
        return CMMNDefinitions(
            id=data.get("id"),
            name=data.get("name"),
            target_namespace=data.get("targetNamespace"),
            expression_language=data.get("expressionLanguage"),
            exporter=data.get("exporter"),
            exporter_version=data.get("exporterVersion"),
            author=data.get("author"),
            creation_date=data.get("creationDate"),
        )

    def _populate_definitions_collections(
        self, definitions: CMMNDefinitions, data: Dict[str, Any]
    ) -> None:
        """Populate definitions with collections."""
        self._populate_imports(definitions, data)
        self._populate_case_file_items(definitions, data)
        self._populate_cases(definitions, data)
        self._populate_processes_and_decisions(definitions, data)
        self._populate_extensions(definitions, data)

    def _populate_imports(
        self, definitions: CMMNDefinitions, data: Dict[str, Any]
    ) -> None:
        """Populate imports."""
        if "imports" in data:
            definitions.imports = [self._parse_import(imp) for imp in data["imports"]]

    def _populate_case_file_items(
        self, definitions: CMMNDefinitions, data: Dict[str, Any]
    ) -> None:
        """Populate case file item definitions."""
        if "caseFileItemDefinitions" in data:
            definitions.case_file_item_definitions = [
                self._parse_case_file_item_definition(cfid)
                for cfid in data["caseFileItemDefinitions"]
            ]

    def _populate_cases(
        self, definitions: CMMNDefinitions, data: Dict[str, Any]
    ) -> None:
        """Populate cases."""
        if "cases" in data:
            definitions.cases = [self._parse_case(case) for case in data["cases"]]

    def _populate_processes_and_decisions(
        self, definitions: CMMNDefinitions, data: Dict[str, Any]
    ) -> None:
        """Populate processes and decisions."""
        if "processes" in data:
            definitions.processes = [
                self._parse_process(proc) for proc in data["processes"]
            ]

        if "decisions" in data:
            definitions.decisions = [
                self._parse_decision(dec) for dec in data["decisions"]
            ]

    def _populate_extensions(
        self, definitions: CMMNDefinitions, data: Dict[str, Any]
    ) -> None:
        """Populate extension elements."""
        if "extensionElements" in data:
            definitions.extension_elements = ExtensionElements(
                elements=data["extensionElements"]
            )

    def _parse_import(self, data: Dict[str, Any]) -> Import:
        """Parse an import from JSON data."""
        return Import(
            id=data.get("id"),
            namespace=data.get("namespace"),
            location=data.get("location"),
            import_type=data.get("importType"),
        )

    def _parse_case_file_item_definition(
        self, data: Dict[str, Any]
    ) -> CaseFileItemDefinition:
        """Parse a case file item definition from JSON data."""
        return CaseFileItemDefinition(
            id=data.get("id"),
            name=data.get("name"),
            description=data.get("description"),
            structure_ref=data.get("structureRef"),
            definitive_property=data.get("definitiveProperty", []),
        )

    def _parse_case(self, data: Dict[str, Any]) -> Case:
        """Parse a case from JSON data."""
        case = Case(
            id=data.get("id"),
            name=data.get("name"),
            description=data.get("description"),
        )

        if "casePlanModel" in data:
            case.case_plan_model = self._parse_case_plan_model(data["casePlanModel"])

        if "caseFileModel" in data:
            case.case_file_model = self._parse_case_file_model(data["caseFileModel"])

        return case

    def _parse_case_plan_model(self, data: Dict[str, Any]) -> CasePlanModel:
        """Parse a case plan model from JSON data."""
        cpm = CasePlanModel(
            id=data.get("id"),
            name=data.get("name"),
            auto_complete=data.get("autoComplete", False),
        )

        self._populate_case_plan_model_elements(cpm, data)
        return cpm

    def _populate_case_plan_model_elements(
        self, cpm: CasePlanModel, data: Dict[str, Any]
    ) -> None:
        """Populate case plan model with its elements."""
        self._populate_plan_items_and_sentries(cpm, data)
        self._populate_stages_and_tasks(cpm, data)
        self._populate_milestones(cpm, data)

    def _populate_plan_items_and_sentries(
        self, cpm: CasePlanModel, data: Dict[str, Any]
    ) -> None:
        """Populate plan items and sentries."""
        if "planItems" in data:
            cpm.plan_items = [self._parse_plan_item(pi) for pi in data["planItems"]]

        if "sentries" in data:
            cpm.sentries = [self._parse_sentry(s) for s in data["sentries"]]

    def _populate_stages_and_tasks(
        self, cpm: CasePlanModel, data: Dict[str, Any]
    ) -> None:
        """Populate stages and tasks."""
        if "stages" in data:
            cpm.stages = [self._parse_stage(s) for s in data["stages"]]

        if "tasks" in data:
            cpm.tasks = [self._parse_task(t) for t in data["tasks"]]

    def _populate_milestones(self, cpm: CasePlanModel, data: Dict[str, Any]) -> None:
        """Populate milestones."""
        if "milestones" in data:
            cpm.milestones = [self._parse_milestone(m) for m in data["milestones"]]

    def _parse_case_file_model(self, data: Dict[str, Any]) -> CaseFileModel:
        """Parse a case file model from JSON data."""
        return CaseFileModel(
            id=data.get("id"),
            name=data.get("name"),
            case_file_items=data.get("caseFileItems", []),
        )

    def _parse_plan_item(self, data: Dict[str, Any]) -> PlanItem:
        """Parse a plan item from JSON data."""
        return PlanItem(
            id=data.get("id"),
            name=data.get("name"),
            definition_ref=data.get("definitionRef"),
            entry_criteria=data.get("entryCriteria", []),
            exit_criteria=data.get("exitCriteria", []),
        )

    def _parse_sentry(self, data: Dict[str, Any]) -> Sentry:
        """Parse a sentry from JSON data."""
        return Sentry(
            id=data.get("id"),
            name=data.get("name"),
            on_part=data.get("onPart", []),
            if_part=data.get("ifPart"),
        )

    def _parse_stage(self, data: Dict[str, Any]) -> Stage:
        """Parse a stage from JSON data."""
        stage = Stage(
            id=data.get("id"),
            name=data.get("name"),
            auto_complete=data.get("autoComplete", False),
        )

        if "planItems" in data:
            stage.plan_items = [self._parse_plan_item(pi) for pi in data["planItems"]]

        return stage

    def _parse_task(self, data: Dict[str, Any]) -> Task:
        """Parse a task from JSON data."""
        task_type = data.get("type", data.get("taskType", "task"))

        base_attrs = {
            "id": data.get("id"),
            "name": data.get("name"),
            "is_blocking": data.get("isBlocking", True),
            "task_type": task_type,
        }

        if task_type == "humanTask":
            return HumanTask(
                **base_attrs,
                performer=data.get("performer"),
                form_key=data.get("formKey"),
            )
        elif task_type == "processTask":
            return ProcessTask(**base_attrs, process_ref=data.get("processRef"))
        elif task_type == "caseTask":
            return CaseTask(**base_attrs, case_ref=data.get("caseRef"))
        elif task_type == "decisionTask":
            return DecisionTask(**base_attrs, decision_ref=data.get("decisionRef"))
        else:
            return Task(**base_attrs)

    def _parse_milestone(self, data: Dict[str, Any]) -> Milestone:
        """Parse a milestone from JSON data."""
        return Milestone(
            id=data.get("id"),
            name=data.get("name"),
            description=data.get("description"),
        )

    def _parse_process(self, data: Dict[str, Any]) -> Process:
        """Parse a process from JSON data."""
        return Process(
            id=data.get("id"),
            name=data.get("name"),
            description=data.get("description"),
            is_executable=data.get("isExecutable", True),
            implementation_type=data.get("implementationType"),
        )

    def _parse_decision(self, data: Dict[str, Any]) -> Decision:
        """Parse a decision from JSON data."""
        return Decision(
            id=data.get("id"),
            name=data.get("name"),
            description=data.get("description"),
            decision_logic=data.get("decisionLogic"),
        )
