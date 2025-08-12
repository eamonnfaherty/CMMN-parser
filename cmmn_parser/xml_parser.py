"""CMMN XML Parser

Handles parsing of CMMN XML format based on the CMMN 1.1 specification.
"""

from typing import Any, Dict

from lxml import etree

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


class XMLParser:
    """Parser for CMMN XML format."""

    CMMN_NAMESPACE = "http://www.omg.org/spec/CMMN/20151109/MODEL"
    CMMNDI_NAMESPACE = "http://www.omg.org/spec/CMMN/20151109/CMMNDI"

    def __init__(self) -> None:
        """Initialize the XML parser."""
        self.namespaces = {"cmmn": self.CMMN_NAMESPACE, "cmmndi": self.CMMNDI_NAMESPACE}

    def parse(self, xml_content: str) -> CMMNDefinitions:
        """Parse CMMN XML content.

        Args:
            xml_content: The XML content as a string

        Returns:
            CMMNDefinitions: Parsed CMMN definitions

        Raises:
            CMMNParsingError: If parsing fails
        """
        try:
            root = etree.fromstring(xml_content.encode("utf-8"))
        except etree.XMLSyntaxError as e:
            raise CMMNParsingError(f"Invalid XML syntax: {e}")

        if root.tag.endswith("definitions"):
            return self._parse_definitions(root)
        else:
            raise CMMNParsingError(
                f"Root element must be 'definitions', got '{root.tag}'"
            )

    def _parse_definitions(self, root: etree.Element) -> CMMNDefinitions:
        """Parse the definitions root element.

        Args:
            root: The definitions XML element

        Returns:
            CMMNDefinitions: Parsed definitions
        """
        definitions = CMMNDefinitions(
            id=root.get("id"),
            name=root.get("name"),
            target_namespace=root.get("targetNamespace"),
            expression_language=root.get("expressionLanguage"),
            exporter=root.get("exporter"),
            exporter_version=root.get("exporterVersion"),
            author=root.get("author"),
            creation_date=root.get("creationDate"),
        )

        for child in root:
            tag = self._strip_namespace(child.tag)

            if tag == "import":
                definitions.imports.append(self._parse_import(child))
            elif tag == "caseFileItemDefinition":
                definitions.case_file_item_definitions.append(
                    self._parse_case_file_item_definition(child)
                )
            elif tag == "case":
                definitions.cases.append(self._parse_case(child))
            elif tag == "process":
                definitions.processes.append(self._parse_process(child))
            elif tag == "decision":
                definitions.decisions.append(self._parse_decision(child))
            elif tag == "extensionElements":
                definitions.extension_elements = self._parse_extension_elements(child)

        return definitions

    def _parse_import(self, element: etree.Element) -> Import:
        """Parse an import element."""
        return Import(
            id=element.get("id"),
            namespace=element.get("namespace"),
            location=element.get("location"),
            import_type=element.get("importType"),
        )

    def _parse_case_file_item_definition(
        self, element: etree.Element
    ) -> CaseFileItemDefinition:
        """Parse a case file item definition element."""
        cfid = CaseFileItemDefinition(
            id=element.get("id"),
            name=element.get("name"),
            structure_ref=element.get("structureRef"),
        )

        for child in element:
            if self._strip_namespace(child.tag) == "definitiveProperty":
                cfid.definitive_property.append(child.get("name", ""))

        return cfid

    def _parse_case(self, element: etree.Element) -> Case:
        """Parse a case element."""
        case = Case(id=element.get("id"), name=element.get("name"))

        for child in element:
            tag = self._strip_namespace(child.tag)

            if tag == "casePlanModel":
                case.case_plan_model = self._parse_case_plan_model(child)
            elif tag == "caseFileModel":
                case.case_file_model = self._parse_case_file_model(child)

        return case

    def _parse_case_plan_model(self, element: etree.Element) -> CasePlanModel:
        """Parse a case plan model element."""
        cpm = CasePlanModel(
            id=element.get("id"),
            name=element.get("name"),
            auto_complete=element.get("autoComplete", "false").lower() == "true",
        )

        for child in element:
            tag = self._strip_namespace(child.tag)

            if tag == "planItem":
                cpm.plan_items.append(self._parse_plan_item(child))
            elif tag == "sentry":
                cpm.sentries.append(self._parse_sentry(child))
            elif tag == "stage":
                cpm.stages.append(self._parse_stage(child))
            elif tag in (
                "task",
                "humanTask",
                "processTask",
                "caseTask",
                "decisionTask",
            ):
                cpm.tasks.append(self._parse_task(child))
            elif tag == "milestone":
                cpm.milestones.append(self._parse_milestone(child))

        return cpm

    def _parse_case_file_model(self, element: etree.Element) -> CaseFileModel:
        """Parse a case file model element."""
        cfm = CaseFileModel(id=element.get("id"), name=element.get("name"))

        for child in element:
            if self._strip_namespace(child.tag) == "caseFileItem":
                cfm.case_file_items.append(child.get("definitionRef", ""))

        return cfm

    def _parse_plan_item(self, element: etree.Element) -> PlanItem:
        """Parse a plan item element."""
        plan_item = PlanItem(
            id=element.get("id"),
            name=element.get("name"),
            definition_ref=element.get("definitionRef"),
        )

        for child in element:
            tag = self._strip_namespace(child.tag)

            if tag == "entryCriterion":
                plan_item.entry_criteria.append(child.get("sentryRef", ""))
            elif tag == "exitCriterion":
                plan_item.exit_criteria.append(child.get("sentryRef", ""))

        return plan_item

    def _parse_sentry(self, element: etree.Element) -> Sentry:
        """Parse a sentry element."""
        sentry = Sentry(id=element.get("id"), name=element.get("name"))

        for child in element:
            tag = self._strip_namespace(child.tag)

            if tag == "planItemOnPart":
                sentry.on_part.append(child.get("sourceRef", ""))
            elif tag == "ifPart":
                sentry.if_part = child.text

        return sentry

    def _parse_stage(self, element: etree.Element) -> Stage:
        """Parse a stage element."""
        stage = Stage(
            id=element.get("id"),
            name=element.get("name"),
            auto_complete=element.get("autoComplete", "false").lower() == "true",
        )

        for child in element:
            if self._strip_namespace(child.tag) == "planItem":
                stage.plan_items.append(self._parse_plan_item(child))

        return stage

    def _parse_task(self, element: etree.Element) -> Task:
        """Parse a task element."""
        tag = self._strip_namespace(element.tag)

        base_attrs = {
            "id": element.get("id"),
            "name": element.get("name"),
            "is_blocking": element.get("isBlocking", "true").lower() == "true",
            "task_type": tag,
        }

        if tag == "humanTask":
            return HumanTask(
                **base_attrs,
                performer=element.get("performer"),
                form_key=element.get("formKey"),
            )
        elif tag == "processTask":
            return ProcessTask(**base_attrs, process_ref=element.get("processRef"))
        elif tag == "caseTask":
            return CaseTask(**base_attrs, case_ref=element.get("caseRef"))
        elif tag == "decisionTask":
            return DecisionTask(**base_attrs, decision_ref=element.get("decisionRef"))
        else:
            return Task(**base_attrs)

    def _parse_milestone(self, element: etree.Element) -> Milestone:
        """Parse a milestone element."""
        return Milestone(id=element.get("id"), name=element.get("name"))

    def _parse_process(self, element: etree.Element) -> Process:
        """Parse a process element."""
        return Process(
            id=element.get("id"),
            name=element.get("name"),
            is_executable=element.get("isExecutable", "true").lower() == "true",
            implementation_type=element.get("implementationType"),
        )

    def _parse_decision(self, element: etree.Element) -> Decision:
        """Parse a decision element."""
        decision = Decision(id=element.get("id"), name=element.get("name"))

        for child in element:
            if self._strip_namespace(child.tag) == "decisionLogic":
                decision.decision_logic = child.text

        return decision

    def _parse_extension_elements(self, element: etree.Element) -> ExtensionElements:
        """Parse extension elements."""
        elements = {}

        for child in element:
            tag = self._strip_namespace(child.tag)
            elements[tag] = self._element_to_dict(child)

        return ExtensionElements(elements=elements)

    def _element_to_dict(self, element: etree.Element) -> Dict[str, Any]:
        """Convert an XML element to a dictionary."""
        result = dict(element.attrib)

        if element.text and element.text.strip():
            result["text"] = element.text.strip()

        children: Dict[str, Any] = {}
        for child in element:
            tag = self._strip_namespace(child.tag)
            if tag not in children:
                children[tag] = []
            children[tag].append(self._element_to_dict(child))

        if children:
            result["children"] = children

        return result

    def _strip_namespace(self, tag: str) -> str:
        """Remove namespace from XML tag."""
        if "}" in tag:
            return tag.split("}", 1)[1]
        return tag
