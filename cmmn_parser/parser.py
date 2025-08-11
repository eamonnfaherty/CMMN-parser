import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union

import jsonschema
from cmmn_parser.models import (
    Case,
    CaseFileItem,
    CaseFileModel,
    CasePlanModel,
    CaseTask,
    CMMNDefinition,
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


class CMMNParseError(Exception):
    pass


class CMMNParser:
    CMMN_NAMESPACE = "http://www.omg.org/spec/CMMN/20151109/MODEL"

    def __init__(self) -> None:
        self.namespaces = {
            "cmmn": self.CMMN_NAMESPACE,
            "cmmndi": "http://www.omg.org/spec/CMMN/20151109/CMMNDI",
            "dc": "http://www.omg.org/spec/CMMN/20151109/DC",
            "di": "http://www.omg.org/spec/CMMN/20151109/DI",
        }
        self._json_schema: Optional[Dict[str, Any]] = None

    def _load_json_schema(self) -> Dict[str, Any]:
        """Load the CMMN JSON schema."""
        if self._json_schema is None:
            schema_path = Path(__file__).parent / "schema.json"
            with open(schema_path, "r") as f:
                self._json_schema = json.load(f)
        return self._json_schema

    def validate_json(self, cmmn_data: Union[str, Dict[str, Any]]) -> bool:
        """Validate CMMN JSON data against the schema."""
        schema = self._load_json_schema()

        if isinstance(cmmn_data, str):
            try:
                data = json.loads(cmmn_data)
            except json.JSONDecodeError as e:
                raise CMMNParseError(f"Invalid JSON format: {e}")
        else:
            data = cmmn_data

        try:
            jsonschema.validate(data, schema)
            return True
        except jsonschema.exceptions.ValidationError as e:
            raise CMMNParseError(f"JSON validation failed: {e.message}")
        except jsonschema.exceptions.SchemaError as e:
            raise CMMNParseError(f"Schema error: {e.message}")

    def parse_file(self, file_path: Union[str, Path]) -> CMMNDefinition:
        """Parse a CMMN file (XML or JSON format)."""
        file_path = Path(file_path)

        if not file_path.exists():
            raise CMMNParseError(f"CMMN file not found: {file_path}")

        try:
            with open(file_path, "r") as f:
                content = f.read()

            # Try to detect format based on file extension and content
            if file_path.suffix.lower() == ".json" or content.strip().startswith("{"):
                return self.parse_json_string(content)
            else:
                # Assume XML format
                return self.parse_xml_string(content)

        except (IOError, OSError) as e:
            raise CMMNParseError(f"Failed to read CMMN file: {e}")

    def parse_xml_string(self, cmmn_text: str) -> CMMNDefinition:
        """Parse CMMN XML string."""
        try:
            root = ET.fromstring(cmmn_text)
            tree = ET.ElementTree(root)
            return self._parse_xml_tree(tree)
        except ET.ParseError as e:
            raise CMMNParseError(f"Failed to parse CMMN XML: {e}")

    def parse_json_file(self, file_path: Union[str, Path]) -> CMMNDefinition:
        """Parse a CMMN JSON file."""
        try:
            with open(file_path, "r") as f:
                content = f.read()
            return self.parse_json_string(content)
        except FileNotFoundError:
            raise CMMNParseError(f"CMMN file not found: {file_path}")
        except (IOError, OSError) as e:
            raise CMMNParseError(f"Failed to read CMMN file: {e}")

    def parse_json_string(self, cmmn_json: str) -> CMMNDefinition:
        """Parse CMMN JSON string."""
        try:
            data = json.loads(cmmn_json)
        except json.JSONDecodeError as e:
            raise CMMNParseError(f"Invalid JSON format: {e}")

        # Validate against schema
        self.validate_json(data)

        # Parse the JSON data
        return self._parse_json_data(data)

    def parse_string(self, cmmn_text: str) -> CMMNDefinition:
        """Parse a CMMN string (auto-detect XML or JSON format)."""
        stripped = cmmn_text.strip()

        if stripped.startswith("{"):
            return self.parse_json_string(cmmn_text)
        else:
            return self.parse_xml_string(cmmn_text)

    def _parse_xml_tree(self, tree: Any) -> CMMNDefinition:
        root = tree.getroot()

        if root is None:
            raise CMMNParseError("No root element found")

        if root.tag != f"{{{self.CMMN_NAMESPACE}}}definitions":
            raise CMMNParseError("Root element must be 'definitions'")

        definition = CMMNDefinition(
            target_namespace=root.get("targetNamespace"),
            expression_language=root.get("expressionLanguage"),
            exporter=root.get("exporter"),
            exporter_version=root.get("exporterVersion"),
        )

        for case_elem in root.findall("cmmn:case", self.namespaces):
            case = self._parse_case(case_elem)
            definition.cases.append(case)

        return definition

    def _parse_case(self, case_elem: ET.Element) -> Case:
        case = Case(id=case_elem.get("id", ""), name=case_elem.get("name"))

        case_file_model_elem = case_elem.find("cmmn:caseFileModel", self.namespaces)
        if case_file_model_elem is not None:
            case.case_file_model = self._parse_case_file_model(case_file_model_elem)

        case_plan_model_elem = case_elem.find("cmmn:casePlanModel", self.namespaces)
        if case_plan_model_elem is not None:
            case.case_plan_model = self._parse_case_plan_model(case_plan_model_elem)

        for role_elem in case_elem.findall("cmmn:caseRoles/cmmn:role", self.namespaces):
            role = Role(id=role_elem.get("id", ""), name=role_elem.get("name"))
            case.case_roles.append(role)

        return case

    def _parse_case_file_model(self, file_model_elem: ET.Element) -> CaseFileModel:
        file_model = CaseFileModel(id=file_model_elem.get("id", ""))

        for item_elem in file_model_elem.findall("cmmn:caseFileItem", self.namespaces):
            item = self._parse_case_file_item(item_elem)
            file_model.case_file_items.append(item)

        return file_model

    def _parse_case_file_item(self, item_elem: ET.Element) -> CaseFileItem:
        item = CaseFileItem(
            id=item_elem.get("id", ""),
            name=item_elem.get("name"),
            definition_type=item_elem.get("definitionType"),
            multiplicity=item_elem.get("multiplicity"),
            source_ref=item_elem.get("sourceRef"),
        )

        target_refs = item_elem.get("targetRefs", "")
        if target_refs:
            item.target_refs = target_refs.split()

        for child_elem in item_elem.findall("cmmn:caseFileItem", self.namespaces):
            child_item = self._parse_case_file_item(child_elem)
            item.children.append(child_item)

        return item

    def _parse_case_plan_model(self, plan_model_elem: ET.Element) -> CasePlanModel:
        plan_model = CasePlanModel(
            id=plan_model_elem.get("id", ""),
            name=plan_model_elem.get("name"),
            auto_complete=plan_model_elem.get("autoComplete", "false").lower()
            == "true",
        )

        self._parse_stage_content(plan_model_elem, plan_model)
        self._parse_task_definitions(plan_model_elem, plan_model)
        self._parse_event_definitions(plan_model_elem, plan_model)
        self._parse_milestone_definitions(plan_model_elem, plan_model)
        self._parse_criteria_definitions(plan_model_elem, plan_model)
        return plan_model

    def _parse_stage_content(self, stage_elem: ET.Element, stage: Stage) -> None:
        for plan_item_elem in stage_elem.findall("cmmn:planItem", self.namespaces):
            plan_item = self._parse_plan_item(plan_item_elem)
            stage.plan_items.append(plan_item)

        for sentry_elem in stage_elem.findall("cmmn:sentry", self.namespaces):
            sentry = self._parse_sentry(sentry_elem)
            stage.sentries.append(sentry)

        for item_elem in stage_elem.findall("cmmn:caseFileItem", self.namespaces):
            item = self._parse_case_file_item(item_elem)
            stage.case_file_items.append(item)

    def _parse_plan_item(self, plan_item_elem: ET.Element) -> PlanItem:
        plan_item = PlanItem(
            id=plan_item_elem.get("id", ""),
            name=plan_item_elem.get("name"),
            definition_ref=plan_item_elem.get("definitionRef"),
        )

        entry_criteria = plan_item_elem.get("entryCriteriaRefs", "")
        if entry_criteria:
            plan_item.entry_criteria = entry_criteria.split()

        exit_criteria = plan_item_elem.get("exitCriteriaRefs", "")
        if exit_criteria:
            plan_item.exit_criteria = exit_criteria.split()

        item_control_elem = plan_item_elem.find("cmmn:itemControl", self.namespaces)
        if item_control_elem is not None:
            plan_item.item_control = self._parse_item_control(item_control_elem)

        return plan_item

    def _parse_item_control(self, control_elem: ET.Element) -> ItemControl:
        control = ItemControl()

        required_rule = control_elem.find("cmmn:requiredRule", self.namespaces)
        if required_rule is not None:
            condition = required_rule.find("cmmn:condition", self.namespaces)
            if condition is not None:
                control.required_rule = condition.text

        repetition_rule = control_elem.find("cmmn:repetitionRule", self.namespaces)
        if repetition_rule is not None:
            condition = repetition_rule.find("cmmn:condition", self.namespaces)
            if condition is not None:
                control.repetition_rule = condition.text

        manual_activation = control_elem.find(
            "cmmn:manualActivationRule", self.namespaces
        )
        if manual_activation is not None:
            condition = manual_activation.find("cmmn:condition", self.namespaces)
            if condition is not None:
                control.manual_activation_rule = condition.text

        return control

    def _parse_sentry(self, sentry_elem: ET.Element) -> Sentry:
        sentry = Sentry(id=sentry_elem.get("id", ""), name=sentry_elem.get("name"))

        for on_part_elem in sentry_elem.findall("cmmn:onPart", self.namespaces):
            on_part = OnPart(
                id=on_part_elem.get("id", ""), source_ref=on_part_elem.get("sourceRef")
            )

            standard_event = on_part_elem.find("cmmn:standardEvent", self.namespaces)
            if standard_event is not None:
                on_part.standard_event = standard_event.text

            sentry.on_parts.append(on_part)

        if_part_elem = sentry_elem.find("cmmn:ifPart", self.namespaces)
        if if_part_elem is not None:
            if_part = IfPart(id=if_part_elem.get("id", ""))
            condition = if_part_elem.find("cmmn:condition", self.namespaces)
            if condition is not None:
                if_part.condition = condition.text
            sentry.if_part = if_part

        return sentry

    def _parse_task_definitions(self, parent_elem: ET.Element, stage: Stage) -> None:
        """Parse task definitions within a stage."""
        # Human Tasks
        for task_elem in parent_elem.findall("cmmn:humanTask", self.namespaces):
            task = HumanTask(
                id=task_elem.get("id", ""),
                name=task_elem.get("name"),
                is_blocking=task_elem.get("isBlocking", "true").lower() == "true",
                performer=task_elem.get("performer"),
            )
            stage._task_definitions.append(task)

        # Process Tasks
        for task_elem in parent_elem.findall("cmmn:processTask", self.namespaces):
            process_task = ProcessTask(
                id=task_elem.get("id", ""),
                name=task_elem.get("name"),
                is_blocking=task_elem.get("isBlocking", "true").lower() == "true",
                process_ref=task_elem.get("processRef"),
            )
            stage._task_definitions.append(process_task)

        # Case Tasks
        for task_elem in parent_elem.findall("cmmn:caseTask", self.namespaces):
            case_task = CaseTask(
                id=task_elem.get("id", ""),
                name=task_elem.get("name"),
                is_blocking=task_elem.get("isBlocking", "true").lower() == "true",
                case_ref=task_elem.get("caseRef"),
            )
            stage._task_definitions.append(case_task)

        # Nested stages
        for stage_elem in parent_elem.findall("cmmn:stage", self.namespaces):
            nested_stage = Stage(
                id=stage_elem.get("id", ""),
                name=stage_elem.get("name"),
                auto_complete=stage_elem.get("autoComplete", "false").lower() == "true",
            )
            self._parse_stage_content(stage_elem, nested_stage)
            self._parse_task_definitions(stage_elem, nested_stage)
            stage._stage_definitions.append(nested_stage)

    def _parse_event_definitions(self, parent_elem: ET.Element, stage: Stage) -> None:
        """Parse event listener definitions within a stage."""
        # Timer Event Listeners
        for event_elem in parent_elem.findall(
            "cmmn:timerEventListener", self.namespaces
        ):
            timer_expr_elem = event_elem.find("cmmn:timerExpression", self.namespaces)
            timer_expr = timer_expr_elem.text if timer_expr_elem is not None else None

            event = TimerEventListener(
                id=event_elem.get("id", ""),
                name=event_elem.get("name"),
                timer_expression=timer_expr,
            )
            stage._event_definitions.append(event)

        # User Event Listeners
        for event_elem in parent_elem.findall(
            "cmmn:userEventListener", self.namespaces
        ):
            auth_roles = event_elem.get("authorizedRoleRefs", "")
            auth_roles_list = auth_roles.split() if auth_roles else []

            user_event = UserEventListener(
                id=event_elem.get("id", ""),
                name=event_elem.get("name"),
                authorized_role_refs=auth_roles_list,
            )
            stage._event_definitions.append(user_event)

    def _parse_milestone_definitions(
        self, parent_elem: ET.Element, stage: Stage
    ) -> None:
        """Parse milestone definitions within a stage."""
        for milestone_elem in parent_elem.findall("cmmn:milestone", self.namespaces):
            milestone = Milestone(
                id=milestone_elem.get("id", ""), name=milestone_elem.get("name")
            )
            stage._milestone_definitions.append(milestone)

    def _parse_criteria_definitions(
        self, parent_elem: ET.Element, stage: Stage
    ) -> None:
        """Parse criteria definitions within a stage."""
        for criterion_elem in parent_elem.findall(
            "cmmn:entryCriterion", self.namespaces
        ):
            criterion = EntryCriterion(
                id=criterion_elem.get("id", ""),
                name=criterion_elem.get("name"),
                sentry_ref=criterion_elem.get("sentryRef"),
            )
            stage._criteria_definitions.append(criterion)

        for criterion_elem in parent_elem.findall(
            "cmmn:exitCriterion", self.namespaces
        ):
            exit_criterion = ExitCriterion(
                id=criterion_elem.get("id", ""),
                name=criterion_elem.get("name"),
                sentry_ref=criterion_elem.get("sentryRef"),
            )
            stage._criteria_definitions.append(exit_criterion)

    # JSON parsing methods
    def _parse_json_data(self, data: Dict[str, Any]) -> CMMNDefinition:
        """Parse CMMN data from JSON format."""
        definitions_data = data["definitions"]

        definition = CMMNDefinition(
            target_namespace=definitions_data.get("targetNamespace"),
            expression_language=definitions_data.get("expressionLanguage"),
            exporter=definitions_data.get("exporter"),
            exporter_version=definitions_data.get("exporterVersion"),
        )

        for case_data in definitions_data["cases"]:
            case = self._parse_json_case(case_data)
            definition.cases.append(case)

        return definition

    def _parse_json_case(self, case_data: Dict[str, Any]) -> Case:
        """Parse a case from JSON data."""
        case = Case(
            id=case_data["id"],
            name=case_data.get("name"),
            documentation=case_data.get("documentation"),
        )

        if "caseFileModel" in case_data:
            case.case_file_model = self._parse_json_case_file_model(
                case_data["caseFileModel"]
            )

        if "casePlanModel" in case_data:
            case.case_plan_model = self._parse_json_case_plan_model(
                case_data["casePlanModel"]
            )

        if "caseRoles" in case_data:
            case.case_roles = [
                self._parse_json_role(role_data) for role_data in case_data["caseRoles"]
            ]

        return case

    def _parse_json_case_file_model(self, data: Dict[str, Any]) -> CaseFileModel:
        """Parse case file model from JSON data."""
        file_model = CaseFileModel(id=data["id"])

        if "caseFileItems" in data:
            file_model.case_file_items = [
                self._parse_json_case_file_item(item_data)
                for item_data in data["caseFileItems"]
            ]

        return file_model

    def _parse_json_case_file_item(self, data: Dict[str, Any]) -> CaseFileItem:
        """Parse case file item from JSON data."""
        item = CaseFileItem(
            id=data["id"],
            name=data.get("name"),
            documentation=data.get("documentation"),
            definition_type=data.get("definitionType"),
            multiplicity=data.get("multiplicity"),
            source_ref=data.get("sourceRef"),
            target_refs=data.get("targetRefs", []),
        )

        if "children" in data:
            item.children = [
                self._parse_json_case_file_item(child_data)
                for child_data in data["children"]
            ]

        return item

    def _parse_json_case_plan_model(self, data: Dict[str, Any]) -> CasePlanModel:
        """Parse case plan model from JSON data."""
        plan_model = CasePlanModel(
            id=data["id"],
            name=data.get("name"),
            documentation=data.get("documentation"),
            auto_complete=data.get("autoComplete", False),
        )

        self._parse_plan_model_items(plan_model, data)
        self._parse_plan_model_definitions(plan_model, data)

        return plan_model

    def _parse_plan_model_items(
        self, plan_model: CasePlanModel, data: Dict[str, Any]
    ) -> None:
        """Parse plan items, sentries, and case file items for a case plan model."""
        if "planItems" in data:
            plan_model.plan_items = [
                self._parse_json_plan_item(item_data) for item_data in data["planItems"]
            ]

        if "sentries" in data:
            plan_model.sentries = [
                self._parse_json_sentry(sentry_data) for sentry_data in data["sentries"]
            ]

        if "caseFileItems" in data:
            plan_model.case_file_items = [
                self._parse_json_case_file_item(item_data)
                for item_data in data["caseFileItems"]
            ]

    def _parse_plan_model_definitions(
        self, plan_model: CasePlanModel, data: Dict[str, Any]
    ) -> None:
        """Parse all definition types for a case plan model."""
        definition_parsers = [
            ("taskDefinitions", self._parse_json_task, plan_model._task_definitions),
            ("eventDefinitions", self._parse_json_event, plan_model._event_definitions),
            (
                "milestoneDefinitions",
                self._parse_json_milestone,
                plan_model._milestone_definitions,
            ),
            ("stageDefinitions", self._parse_json_stage, plan_model._stage_definitions),
            (
                "criteriaDefinitions",
                self._parse_json_criterion,
                plan_model._criteria_definitions,
            ),
        ]

        for key, parser, definition_list in definition_parsers:
            self._parse_definition_list(data, key, parser, definition_list)

    def _parse_definition_list(
        self,
        data: Dict[str, Any],
        key: str,
        parser: Callable[[Dict[str, Any]], Any],
        definition_list: Any,
    ) -> None:
        """Parse a list of definitions using the provided parser function."""
        if key in data:
            for item_data in data[key]:
                item = parser(item_data)
                definition_list.append(item)

    def _parse_json_plan_item(self, data: Dict[str, Any]) -> PlanItem:
        """Parse plan item from JSON data."""
        plan_item = PlanItem(
            id=data["id"],
            name=data.get("name"),
            documentation=data.get("documentation"),
            definition_ref=data.get("definitionRef"),
            entry_criteria=data.get("entryCriteria", []),
            exit_criteria=data.get("exitCriteria", []),
            reactivation_criteria=data.get("reactivationCriteria", []),
        )

        if "itemControl" in data:
            plan_item.item_control = self._parse_json_item_control(data["itemControl"])

        return plan_item

    def _parse_json_item_control(self, data: Dict[str, Any]) -> ItemControl:
        """Parse item control from JSON data."""
        return ItemControl(
            required_rule=data.get("requiredRule"),
            repetition_rule=data.get("repetitionRule"),
            manual_activation_rule=data.get("manualActivationRule"),
        )

    def _parse_json_sentry(self, data: Dict[str, Any]) -> Sentry:
        """Parse sentry from JSON data."""
        sentry = Sentry(
            id=data["id"],
            name=data.get("name"),
            documentation=data.get("documentation"),
        )

        if "onParts" in data:
            sentry.on_parts = [
                self._parse_json_on_part(on_part_data)
                for on_part_data in data["onParts"]
            ]

        if "ifPart" in data:
            sentry.if_part = self._parse_json_if_part(data["ifPart"])

        return sentry

    def _parse_json_on_part(self, data: Dict[str, Any]) -> OnPart:
        """Parse on part from JSON data."""
        return OnPart(
            id=data["id"],
            source_ref=data.get("sourceRef"),
            standard_event=data.get("standardEvent"),
        )

    def _parse_json_if_part(self, data: Dict[str, Any]) -> IfPart:
        """Parse if part from JSON data."""
        return IfPart(id=data["id"], condition=data.get("condition"))

    def _parse_json_task(
        self, data: Dict[str, Any]
    ) -> Union[HumanTask, ProcessTask, CaseTask]:
        """Parse task from JSON data."""
        base_attrs = {
            "id": data["id"],
            "name": data.get("name"),
            "documentation": data.get("documentation"),
            "is_blocking": data.get("isBlocking", True),
        }

        if "performer" in data:
            return HumanTask(**base_attrs, performer=data["performer"])
        elif "processRef" in data:
            return ProcessTask(**base_attrs, process_ref=data["processRef"])
        elif "caseRef" in data:
            return CaseTask(**base_attrs, case_ref=data["caseRef"])
        else:
            return HumanTask(**base_attrs)

    def _parse_json_event(
        self, data: Dict[str, Any]
    ) -> Union[TimerEventListener, UserEventListener]:
        """Parse event listener from JSON data."""
        base_attrs = {
            "id": data["id"],
            "name": data.get("name"),
            "documentation": data.get("documentation"),
        }

        if "timerExpression" in data:
            return TimerEventListener(
                **base_attrs, timer_expression=data["timerExpression"]
            )
        elif "authorizedRoleRefs" in data:
            return UserEventListener(
                **base_attrs, authorized_role_refs=data["authorizedRoleRefs"]
            )
        else:
            return UserEventListener(**base_attrs)

    def _parse_json_milestone(self, data: Dict[str, Any]) -> Milestone:
        """Parse milestone from JSON data."""
        return Milestone(
            id=data["id"],
            name=data.get("name"),
            documentation=data.get("documentation"),
        )

    def _parse_json_stage(self, data: Dict[str, Any]) -> Stage:
        """Parse stage from JSON data."""
        stage = Stage(
            id=data["id"],
            name=data.get("name"),
            documentation=data.get("documentation"),
            auto_complete=data.get("autoComplete", False),
        )

        if "planItems" in data:
            stage.plan_items = [
                self._parse_json_plan_item(item_data) for item_data in data["planItems"]
            ]

        if "sentries" in data:
            stage.sentries = [
                self._parse_json_sentry(sentry_data) for sentry_data in data["sentries"]
            ]

        if "caseFileItems" in data:
            stage.case_file_items = [
                self._parse_json_case_file_item(item_data)
                for item_data in data["caseFileItems"]
            ]

        return stage

    def _parse_json_criterion(
        self, data: Dict[str, Any]
    ) -> Union[EntryCriterion, ExitCriterion]:
        """Parse criterion from JSON data."""
        base_attrs = {
            "id": data["id"],
            "name": data.get("name"),
            "documentation": data.get("documentation"),
            "sentry_ref": data.get("sentryRef"),
        }

        # Determine criterion type based on the data or add a type field to the schema
        if data.get("type") == "exit":
            return ExitCriterion(**base_attrs)
        else:
            return EntryCriterion(**base_attrs)

    def _parse_json_role(self, data: Dict[str, Any]) -> Role:
        """Parse role from JSON data."""
        return Role(id=data["id"], name=data.get("name"))
