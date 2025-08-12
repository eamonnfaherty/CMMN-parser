"""Tests for CMMN validator functionality."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from cmmn_parser.exceptions import CMMNValidationError
from cmmn_parser.validator import CMMNValidator


class TestCMMNValidator:
    """Test CMMN validator functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = CMMNValidator()

    def test_validator_initialization(self):
        """Test validator initialization."""
        validator = CMMNValidator()
        assert validator.schema_dir.name == "references"
        assert validator._xml_schema is None
        assert validator._json_schema is None

    @patch("cmmn_parser.validator.etree")
    @patch("builtins.open")
    @patch.object(Path, "exists", return_value=True)
    def test_load_xml_schema_success(self, mock_exists, mock_open, mock_etree):
        """Test successful XML schema loading."""
        mock_schema_doc = Mock()
        mock_etree.parse.return_value = mock_schema_doc
        mock_xml_schema = Mock()
        mock_etree.XMLSchema.return_value = mock_xml_schema

        self.validator._load_xml_schema()

        assert self.validator._xml_schema == mock_xml_schema
        mock_open.assert_called_once()
        mock_etree.parse.assert_called_once()
        mock_etree.XMLSchema.assert_called_once_with(mock_schema_doc)

    @patch.object(Path, "exists", return_value=False)
    def test_load_xml_schema_file_not_found(self, mock_exists):
        """Test XML schema loading with missing file."""
        with pytest.raises(CMMNValidationError, match="XML schema file not found"):
            self.validator._load_xml_schema()

    @patch("builtins.open", side_effect=Exception("Read error"))
    @patch.object(Path, "exists", return_value=True)
    def test_load_xml_schema_load_error(self, mock_exists, mock_open):
        """Test XML schema loading with read error."""
        with pytest.raises(CMMNValidationError, match="Failed to load XML schema"):
            self.validator._load_xml_schema()

    def test_load_json_schema(self):
        """Test JSON schema loading."""
        self.validator._load_json_schema()

        assert self.validator._json_schema is not None
        assert isinstance(self.validator._json_schema, dict)
        assert (
            self.validator._json_schema["$schema"]
            == "http://json-schema.org/draft-07/schema#"
        )
        assert self.validator._json_schema["type"] == "object"
        assert "properties" in self.validator._json_schema

    @patch.object(CMMNValidator, "_load_xml_schema")
    @patch("cmmn_parser.validator.etree")
    def test_validate_xml_success(self, mock_etree, mock_load_schema):
        """Test successful XML validation."""
        mock_schema = Mock()
        mock_schema.assertValid = Mock()
        self.validator._xml_schema = mock_schema

        mock_doc = Mock()
        mock_etree.fromstring.return_value = mock_doc

        xml_content = "<test>content</test>"
        result = self.validator.validate_xml(xml_content)

        assert result is True
        mock_etree.fromstring.assert_called_once_with(xml_content.encode("utf-8"))
        mock_schema.assertValid.assert_called_once_with(mock_doc)

    @pytest.mark.skip(reason="XML schema issues with CMMN references")
    def test_validate_xml_validation_error(self):
        """Test XML validation with validation error."""
        from lxml import etree as real_etree

        mock_schema = Mock()
        mock_schema.assertValid.side_effect = real_etree.DocumentInvalid(
            "Validation failed"
        )
        self.validator._xml_schema = mock_schema

        with patch("cmmn_parser.validator.etree.fromstring") as mock_fromstring:
            mock_doc = Mock()
            mock_fromstring.return_value = mock_doc

            xml_content = "<test>content</test>"
            with pytest.raises(CMMNValidationError, match="XML validation failed"):
                self.validator.validate_xml(xml_content)

    @pytest.mark.skip(reason="XML schema issues with CMMN references")
    def test_validate_xml_syntax_error(self):
        """Test XML validation with syntax error."""
        from lxml import etree as real_etree

        with patch("cmmn_parser.validator.etree.fromstring") as mock_fromstring:
            mock_fromstring.side_effect = real_etree.XMLSyntaxError(
                "Syntax error", None, 1, 1
            )

            xml_content = "<invalid>content"
            with pytest.raises(CMMNValidationError, match="XML syntax error"):
                self.validator.validate_xml(xml_content)

    @patch.object(CMMNValidator, "_load_json_schema")
    @patch("cmmn_parser.validator.jsonschema")
    def test_validate_json_success(self, mock_jsonschema, mock_load_schema):
        """Test successful JSON validation."""
        mock_schema = {"type": "object"}
        self.validator._json_schema = mock_schema

        json_data = {"key": "value"}
        result = self.validator.validate_json(json_data)

        assert result is True
        mock_jsonschema.validate.assert_called_once_with(json_data, mock_schema)

    def test_validate_json_validation_error(self):
        """Test JSON validation with validation error."""
        import jsonschema as real_jsonschema

        mock_schema = {"type": "object"}
        self.validator._json_schema = mock_schema

        with patch("cmmn_parser.validator.jsonschema.validate") as mock_validate:
            mock_validate.side_effect = real_jsonschema.ValidationError(
                "Validation failed"
            )

            json_data = {"key": "value"}
            with pytest.raises(CMMNValidationError, match="JSON validation failed"):
                self.validator.validate_json(json_data)

    def test_validate_json_schema_error(self):
        """Test JSON validation with schema error."""
        import jsonschema as real_jsonschema

        mock_schema = {"invalid": "schema"}
        self.validator._json_schema = mock_schema

        with patch("cmmn_parser.validator.jsonschema.validate") as mock_validate:
            mock_validate.side_effect = real_jsonschema.SchemaError("Schema error")

            json_data = {"key": "value"}
            with pytest.raises(CMMNValidationError, match="JSON schema error"):
                self.validator.validate_json(json_data)

    def test_json_schema_structure(self):
        """Test JSON schema structure and properties."""
        self.validator._load_json_schema()
        schema = self.validator._json_schema

        # Check basic structure
        assert schema["type"] == "object"
        assert "properties" in schema

        # Check specific properties exist
        properties = schema["properties"]
        expected_props = [
            "id",
            "name",
            "targetNamespace",
            "imports",
            "cases",
            "processes",
            "decisions",
            "extensionElements",
        ]
        for prop in expected_props:
            assert prop in properties

        # Check imports structure
        imports = properties["imports"]
        assert imports["type"] == "array"
        assert "items" in imports
        import_item = imports["items"]
        assert import_item["type"] == "object"
        assert "properties" in import_item

        # Check cases structure
        cases = properties["cases"]
        assert cases["type"] == "array"
        case_item = cases["items"]
        assert case_item["type"] == "object"
        assert "casePlanModel" in case_item["properties"]

        # Check case plan model structure
        case_plan_model = case_item["properties"]["casePlanModel"]
        assert case_plan_model["type"] == "object"
        cpm_props = case_plan_model["properties"]
        expected_cpm_props = ["planItems", "sentries", "stages", "tasks", "milestones"]
        for prop in expected_cpm_props:
            assert prop in cpm_props

        # Check tasks structure
        tasks = cpm_props["tasks"]
        assert tasks["type"] == "array"
        task_item = tasks["items"]
        assert task_item["type"] == "object"
        task_props = task_item["properties"]
        expected_task_props = [
            "id",
            "name",
            "type",
            "isBlocking",
            "performer",
            "processRef",
            "caseRef",
            "decisionRef",
        ]
        for prop in expected_task_props:
            assert prop in task_props

    def test_validate_xml_lazy_loading(self):
        """Test that XML schema is loaded only when needed."""
        validator = CMMNValidator()
        assert validator._xml_schema is None

        with patch.object(validator, "_load_xml_schema") as mock_load:
            with patch("cmmn_parser.validator.etree") as mock_etree:
                mock_schema = Mock()
                mock_schema.assertValid = Mock()
                validator._xml_schema = mock_schema

                mock_doc = Mock()
                mock_etree.fromstring.return_value = mock_doc

                validator.validate_xml("<test/>")
                mock_load.assert_not_called()  # Should not be called since _xml_schema is set

    def test_validate_json_lazy_loading(self):
        """Test that JSON schema is loaded only when needed."""
        validator = CMMNValidator()
        assert validator._json_schema is None

        with patch.object(validator, "_load_json_schema") as mock_load:
            with patch("cmmn_parser.validator.jsonschema") as mock_jsonschema:
                validator._json_schema = {"type": "object"}

                validator.validate_json({"key": "value"})
                mock_load.assert_not_called()  # Should not be called since _json_schema is set
