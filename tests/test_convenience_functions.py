import tempfile
from pathlib import Path

import pytest

import cmmn_parser
from cmmn_parser import CMMNParseError
from cmmn_parser.models import CMMNDefinition


class TestConvenienceFunctions:

    @pytest.fixture
    def sample_cmmn_file(self):
        return Path(__file__).parent / "fixtures" / "sample_cmmn.xml"

    @pytest.fixture
    def sample_cmmn_content(self, sample_cmmn_file):
        return sample_cmmn_file.read_text()

    def test_parse_cmmn_file_function(self, sample_cmmn_file):
        """Test the convenience function for parsing files."""
        definition = cmmn_parser.parse_cmmn_file(sample_cmmn_file)

        assert isinstance(definition, CMMNDefinition)
        assert definition.target_namespace == "http://example.com/cmmn"
        assert len(definition.cases) == 1
        assert definition.cases[0].id == "Case_1"

    def test_parse_cmmn_string_function(self, sample_cmmn_content):
        """Test the convenience function for parsing strings."""
        definition = cmmn_parser.parse_cmmn_string(sample_cmmn_content)

        assert isinstance(definition, CMMNDefinition)
        assert definition.target_namespace == "http://example.com/cmmn"
        assert len(definition.cases) == 1
        assert definition.cases[0].id == "Case_1"

    def test_parse_cmmn_file_with_path_object(self, sample_cmmn_file):
        """Test convenience function with Path object."""
        path_obj = Path(sample_cmmn_file)
        definition = cmmn_parser.parse_cmmn_file(path_obj)

        assert isinstance(definition, CMMNDefinition)
        assert len(definition.cases) == 1

    def test_parse_cmmn_file_with_string_path(self, sample_cmmn_file):
        """Test convenience function with string path."""
        string_path = str(sample_cmmn_file)
        definition = cmmn_parser.parse_cmmn_file(string_path)

        assert isinstance(definition, CMMNDefinition)
        assert len(definition.cases) == 1

    def test_parse_cmmn_file_error_handling(self):
        """Test error handling in convenience function."""
        with pytest.raises(CMMNParseError):
            cmmn_parser.parse_cmmn_file("/non/existent/file.cmmn")

    def test_parse_cmmn_string_error_handling(self):
        """Test error handling in string parsing convenience function."""
        invalid_xml = "<invalid>xml without closing tag"

        with pytest.raises(CMMNParseError):
            cmmn_parser.parse_cmmn_string(invalid_xml)

    def test_parse_cmmn_string_empty_input(self):
        """Test parsing empty string."""
        with pytest.raises(CMMNParseError):
            cmmn_parser.parse_cmmn_string("")

    def test_parse_cmmn_string_minimal_valid(self):
        """Test parsing minimal valid CMMN string."""
        minimal_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <cmmn:definitions xmlns:cmmn="http://www.omg.org/spec/CMMN/20151109/MODEL">
            <cmmn:case id="TestCase">
                <cmmn:casePlanModel id="TestPlan"/>
            </cmmn:case>
        </cmmn:definitions>"""

        definition = cmmn_parser.parse_cmmn_string(minimal_xml)
        assert isinstance(definition, CMMNDefinition)
        assert len(definition.cases) == 1
        assert definition.cases[0].id == "TestCase"

    def test_temporary_file_parsing(self, sample_cmmn_content):
        """Test parsing with temporary files."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".cmmn", delete=False) as tf:
            tf.write(sample_cmmn_content)
            tf.flush()

            definition = cmmn_parser.parse_cmmn_file(tf.name)
            assert isinstance(definition, CMMNDefinition)
            assert len(definition.cases) == 1

    def test_unicode_content_parsing(self):
        """Test parsing CMMN with unicode content."""
        unicode_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <cmmn:definitions xmlns:cmmn="http://www.omg.org/spec/CMMN/20151109/MODEL">
            <cmmn:case id="UnicodeCase" name="测试案例">
                <cmmn:casePlanModel id="UnicodePlan" name="测试计划"/>
            </cmmn:case>
        </cmmn:definitions>"""

        definition = cmmn_parser.parse_cmmn_string(unicode_xml)
        assert definition.cases[0].name == "测试案例"
        assert definition.cases[0].case_plan_model.name == "测试计划"
