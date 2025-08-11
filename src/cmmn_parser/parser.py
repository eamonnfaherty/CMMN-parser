import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Union

from .models import (
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

    def parse_file(self, file_path: Union[str, Path]) -> CMMNDefinition:
        try:
            tree = ET.parse(str(file_path))
            return self._parse_tree(tree)
        except ET.ParseError as e:
            raise CMMNParseError(f"Failed to parse CMMN file: {e}")
        except FileNotFoundError:
            raise CMMNParseError(f"CMMN file not found: {file_path}")

    def parse_string(self, cmmn_text: str) -> CMMNDefinition:
        try:
            root = ET.fromstring(cmmn_text)
            tree = ET.ElementTree(root)
            return self._parse_tree(tree)
        except ET.ParseError as e:
            raise CMMNParseError(f"Failed to parse CMMN text: {e}")

    def _parse_tree(self, tree: Any) -> CMMNDefinition:
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
