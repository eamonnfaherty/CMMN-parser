"""Integration tests for CMMN parser."""

import json
import os
import tempfile

import pytest

from cmmn_parser import CMMNParser, parse_cmmn_file, parse_cmmn_string
from cmmn_parser.exceptions import CMMNParsingError, CMMNValidationError
from cmmn_parser.models import CMMNDefinitions


class TestIntegration:
    """Integration tests for the complete CMMN parser."""

    def setup_method(self):
        """Set up test fixtures."""
        self.sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/CMMN/20151109/MODEL"
             id="enterprise_case" 
             name="Enterprise Case Management"
             targetNamespace="http://enterprise.example.com/cmmn"
             exporter="Enterprise Modeler" 
             exporterVersion="2.0"
             author="System Analyst"
             creationDate="2023-12-01">
    
    <import id="import1" 
            namespace="http://external.example.com" 
            location="external.xsd" 
            importType="http://external.example.com/type"/>
    
    <caseFileItemDefinition id="customer_data" 
                           name="Customer Data" 
                           structureRef="Customer">
        <definitiveProperty name="customerId"/>
        <definitiveProperty name="customerType"/>
    </caseFileItemDefinition>
    
    <case id="customer_onboarding" name="Customer Onboarding Process">
        <caseFileModel id="case_file_model">
            <caseFileItem definitionRef="customer_data"/>
        </caseFileModel>
        
        <casePlanModel id="main_plan" name="Main Case Plan" autoComplete="false">
            <planItem id="pi_verification" 
                     name="Verification Process" 
                     definitionRef="verification_stage">
                <entryCriterion sentryRef="start_sentry"/>
            </planItem>
            
            <planItem id="pi_approval" 
                     name="Approval Process" 
                     definitionRef="approval_task">
                <entryCriterion sentryRef="verification_complete"/>
            </planItem>
            
            <sentry id="start_sentry" name="Start Condition">
                <planItemOnPart sourceRef="data_collection"/>
                <ifPart>customer_data.customerId != null</ifPart>
            </sentry>
            
            <sentry id="verification_complete" name="Verification Complete">
                <planItemOnPart sourceRef="verification_stage"/>
            </sentry>
            
            <stage id="verification_stage" 
                   name="Customer Verification" 
                   autoComplete="true">
                <planItem id="pi_identity_check" 
                         name="Identity Check" 
                         definitionRef="identity_task"/>
                <planItem id="pi_credit_check" 
                         name="Credit Check" 
                         definitionRef="credit_task"/>
            </stage>
            
            <humanTask id="identity_task" 
                      name="Verify Customer Identity" 
                      performer="verification_team"
                      formKey="identity_form"
                      isBlocking="true"/>
            
            <processTask id="credit_task" 
                        name="Run Credit Check" 
                        processRef="credit_check_process"/>
            
            <humanTask id="approval_task" 
                      name="Final Approval" 
                      performer="manager"
                      formKey="approval_form"/>
            
            <milestone id="onboarding_complete" 
                      name="Customer Onboarding Complete"/>
        </casePlanModel>
    </case>
    
    <process id="credit_check_process" 
            name="Credit Check Process" 
            isExecutable="true"
            implementationType="external_service"/>
    
    <decision id="risk_decision" 
             name="Risk Assessment Decision">
        <decisionLogic>
            if (credit_score > 700) return "LOW_RISK";
            else if (credit_score > 600) return "MEDIUM_RISK";
            else return "HIGH_RISK";
        </decisionLogic>
    </decision>
</definitions>"""

        self.sample_json = {
            "id": "enterprise_case",
            "name": "Enterprise Case Management",
            "targetNamespace": "http://enterprise.example.com/cmmn",
            "exporter": "Enterprise Modeler",
            "exporterVersion": "2.0",
            "author": "System Analyst",
            "creationDate": "2023-12-01",
            "imports": [
                {
                    "id": "import1",
                    "namespace": "http://external.example.com",
                    "location": "external.xsd",
                    "importType": "http://external.example.com/type",
                }
            ],
            "caseFileItemDefinitions": [
                {
                    "id": "customer_data",
                    "name": "Customer Data",
                    "structureRef": "Customer",
                    "definitiveProperty": ["customerId", "customerType"],
                }
            ],
            "cases": [
                {
                    "id": "customer_onboarding",
                    "name": "Customer Onboarding Process",
                    "caseFileModel": {
                        "id": "case_file_model",
                        "caseFileItems": ["customer_data"],
                    },
                    "casePlanModel": {
                        "id": "main_plan",
                        "name": "Main Case Plan",
                        "autoComplete": False,
                        "planItems": [
                            {
                                "id": "pi_verification",
                                "name": "Verification Process",
                                "definitionRef": "verification_stage",
                                "entryCriteria": ["start_sentry"],
                            },
                            {
                                "id": "pi_approval",
                                "name": "Approval Process",
                                "definitionRef": "approval_task",
                                "entryCriteria": ["verification_complete"],
                            },
                        ],
                        "sentries": [
                            {
                                "id": "start_sentry",
                                "name": "Start Condition",
                                "onPart": ["data_collection"],
                                "ifPart": "customer_data.customerId != null",
                            },
                            {
                                "id": "verification_complete",
                                "name": "Verification Complete",
                                "onPart": ["verification_stage"],
                            },
                        ],
                        "stages": [
                            {
                                "id": "verification_stage",
                                "name": "Customer Verification",
                                "autoComplete": True,
                                "planItems": [
                                    {
                                        "id": "pi_identity_check",
                                        "name": "Identity Check",
                                        "definitionRef": "identity_task",
                                    },
                                    {
                                        "id": "pi_credit_check",
                                        "name": "Credit Check",
                                        "definitionRef": "credit_task",
                                    },
                                ],
                            }
                        ],
                        "tasks": [
                            {
                                "id": "identity_task",
                                "name": "Verify Customer Identity",
                                "type": "humanTask",
                                "performer": "verification_team",
                                "formKey": "identity_form",
                                "isBlocking": True,
                            },
                            {
                                "id": "credit_task",
                                "name": "Run Credit Check",
                                "type": "processTask",
                                "processRef": "credit_check_process",
                            },
                            {
                                "id": "approval_task",
                                "name": "Final Approval",
                                "type": "humanTask",
                                "performer": "manager",
                                "formKey": "approval_form",
                            },
                        ],
                        "milestones": [
                            {
                                "id": "onboarding_complete",
                                "name": "Customer Onboarding Complete",
                            }
                        ],
                    },
                }
            ],
            "processes": [
                {
                    "id": "credit_check_process",
                    "name": "Credit Check Process",
                    "isExecutable": True,
                    "implementationType": "external_service",
                }
            ],
            "decisions": [
                {
                    "id": "risk_decision",
                    "name": "Risk Assessment Decision",
                    "decisionLogic": 'if (credit_score > 700) return "LOW_RISK"; else if (credit_score > 600) return "MEDIUM_RISK"; else return "HIGH_RISK";',
                }
            ],
        }

    def test_parse_complex_xml_string(self):
        """Test parsing complex XML string."""
        result = parse_cmmn_string(self.sample_xml)

        self._verify_parsed_definitions(result)

    def test_parse_complex_json_string(self):
        """Test parsing complex JSON string."""
        json_string = json.dumps(self.sample_json)
        result = parse_cmmn_string(json_string)

        self._verify_parsed_definitions(result)

    def test_parse_xml_file(self):
        """Test parsing XML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(self.sample_xml)
            temp_path = f.name

        try:
            result = parse_cmmn_file(temp_path)
            self._verify_parsed_definitions(result)
        finally:
            os.unlink(temp_path)

    def test_parse_json_file(self):
        """Test parsing JSON file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(self.sample_json, f)
            temp_path = f.name

        try:
            result = parse_cmmn_file(temp_path)
            self._verify_parsed_definitions(result)
        finally:
            os.unlink(temp_path)

    def test_xml_to_dict_conversion(self):
        """Test converting parsed XML to dictionary."""
        result = parse_cmmn_string(self.sample_xml)
        data = result.to_dict()

        # Verify basic structure
        assert data["id"] == "enterprise_case"
        assert data["name"] == "Enterprise Case Management"
        assert data["targetNamespace"] == "http://enterprise.example.com/cmmn"

        # Verify complex nested structures
        assert len(data["cases"]) == 1
        case = data["cases"][0]
        assert case["id"] == "customer_onboarding"

        cpm = case["casePlanModel"]
        assert cpm["id"] == "main_plan"
        assert len(cpm["tasks"]) == 3
        assert len(cpm["stages"]) == 1
        assert len(cpm["sentries"]) == 2

        # Verify task types are correctly identified
        human_tasks = [t for t in cpm["tasks"] if t.get("type") == "humanTask"]
        process_tasks = [t for t in cpm["tasks"] if t.get("type") == "processTask"]
        assert len(human_tasks) == 2
        assert len(process_tasks) == 1

    def test_round_trip_xml_to_json(self):
        """Test round-trip conversion from XML to JSON and back."""
        # Parse XML
        xml_result = parse_cmmn_string(self.sample_xml)

        # Convert to dictionary (JSON representation)
        data = xml_result.to_dict()

        # Parse JSON representation
        json_result = parse_cmmn_string(json.dumps(data))

        # Compare key properties
        assert xml_result.id == json_result.id
        assert xml_result.name == json_result.name
        assert len(xml_result.cases) == len(json_result.cases)
        assert len(xml_result.processes) == len(json_result.processes)
        assert len(xml_result.decisions) == len(json_result.decisions)

    def test_parser_with_different_formats(self):
        """Test parser with explicit format specification."""
        parser = CMMNParser()

        # Parse XML with explicit format
        xml_result = parser.parse_string(self.sample_xml, "xml")
        assert xml_result.id == "enterprise_case"

        # Parse JSON with explicit format
        json_string = json.dumps(self.sample_json)
        json_result = parser.parse_string(json_string, "json")
        assert json_result.id == "enterprise_case"

        # Verify they parsed to equivalent structures
        assert xml_result.id == json_result.id
        assert xml_result.name == json_result.name

    def test_error_handling_integration(self):
        """Test error handling in integration scenarios."""
        parser = CMMNParser()

        # Test invalid XML
        invalid_xml = "<definitions><case><unclosed></case></definitions>"
        with pytest.raises(CMMNParsingError):
            parser.parse_xml_string(invalid_xml)

        # Test invalid JSON
        invalid_json = '{"id": "test", "invalid": json}'
        with pytest.raises(CMMNParsingError):
            parser.parse_json_string(invalid_json)

        # Test non-existent file
        with pytest.raises(FileNotFoundError):
            parser.parse_file("non_existent_file.xml")

    def test_convenience_functions(self):
        """Test convenience functions work correctly."""
        # Test parse_cmmn_string with auto-detection
        xml_result = parse_cmmn_string(self.sample_xml, "auto")
        json_result = parse_cmmn_string(json.dumps(self.sample_json), "auto")

        assert xml_result.id == json_result.id

        # Test with file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(self.sample_xml)
            temp_path = f.name

        try:
            file_result = parse_cmmn_file(temp_path, "auto")
            assert file_result.id == xml_result.id
        finally:
            os.unlink(temp_path)

    def _verify_parsed_definitions(self, result):
        """Helper method to verify parsed definitions."""
        assert isinstance(result, CMMNDefinitions)

        # Verify basic properties
        assert result.id == "enterprise_case"
        assert result.name == "Enterprise Case Management"
        assert result.target_namespace == "http://enterprise.example.com/cmmn"
        assert result.exporter == "Enterprise Modeler"
        assert result.exporter_version == "2.0"
        assert result.author == "System Analyst"
        assert result.creation_date == "2023-12-01"

        # Verify imports
        assert len(result.imports) == 1
        import_obj = result.imports[0]
        assert import_obj.id == "import1"
        assert import_obj.namespace == "http://external.example.com"

        # Verify case file item definitions
        assert len(result.case_file_item_definitions) == 1
        cfid = result.case_file_item_definitions[0]
        assert cfid.id == "customer_data"
        assert cfid.name == "Customer Data"
        assert len(cfid.definitive_property) == 2

        # Verify cases
        assert len(result.cases) == 1
        case = result.cases[0]
        assert case.id == "customer_onboarding"
        assert case.name == "Customer Onboarding Process"

        # Verify case plan model
        assert case.case_plan_model is not None
        cpm = case.case_plan_model
        assert cpm.id == "main_plan"
        assert cpm.auto_complete is False

        # Verify plan items
        assert len(cpm.plan_items) == 2
        pi_verification = next(
            pi for pi in cpm.plan_items if pi.id == "pi_verification"
        )
        assert pi_verification.definition_ref == "verification_stage"

        # Verify sentries
        assert len(cpm.sentries) == 2
        start_sentry = next(s for s in cpm.sentries if s.id == "start_sentry")
        assert start_sentry.if_part == "customer_data.customerId != null"

        # Verify stages
        assert len(cpm.stages) == 1
        stage = cpm.stages[0]
        assert stage.id == "verification_stage"
        assert stage.auto_complete is True
        assert len(stage.plan_items) == 2

        # Verify tasks
        assert len(cpm.tasks) == 3
        identity_task = next(t for t in cpm.tasks if t.id == "identity_task")
        assert identity_task.name == "Verify Customer Identity"

        # Verify milestones
        assert len(cpm.milestones) == 1
        milestone = cpm.milestones[0]
        assert milestone.id == "onboarding_complete"

        # Verify processes
        assert len(result.processes) == 1
        process = result.processes[0]
        assert process.id == "credit_check_process"
        assert process.is_executable is True

        # Verify decisions
        assert len(result.decisions) == 1
        decision = result.decisions[0]
        assert decision.id == "risk_decision"
        assert "credit_score" in decision.decision_logic
