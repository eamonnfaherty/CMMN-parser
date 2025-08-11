"""
JSON validation functions for CMMN documents.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Union, cast

import jsonschema

from .parser import CMMNParseError


def load_cmmn_schema() -> Dict[str, Any]:
    """Load the CMMN JSON schema from the schema file."""
    schema_path = Path(__file__).parent / "schema.json"
    with open(schema_path, "r") as f:
        return cast(Dict[str, Any], json.load(f))


def validate_cmmn_json(cmmn_data: Union[str, Dict[str, Any]]) -> bool:
    """
    Validate CMMN JSON data against the schema.

    Args:
        cmmn_data: Either a JSON string or a dictionary containing CMMN data

    Returns:
        True if validation passes

    Raises:
        CMMNParseError: If the JSON is invalid or doesn't match the schema
    """
    schema = load_cmmn_schema()

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


def validate_cmmn_json_file(file_path: Union[str, Path]) -> bool:
    """
    Validate a CMMN JSON file against the schema.

    Args:
        file_path: Path to the JSON file to validate

    Returns:
        True if validation passes

    Raises:
        CMMNParseError: If the file doesn't exist, is invalid JSON, or doesn't match the schema
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise CMMNParseError(f"File not found: {file_path}")

    try:
        with open(file_path, "r") as f:
            content = f.read()
        return validate_cmmn_json(content)
    except (IOError, OSError) as e:
        raise CMMNParseError(f"Failed to read file: {e}")


def get_validation_errors(cmmn_data: Union[str, Dict[str, Any]]) -> List[str]:
    """
    Get a list of validation errors without raising an exception.

    Args:
        cmmn_data: Either a JSON string or a dictionary containing CMMN data

    Returns:
        List of validation error messages (empty list if valid)
    """
    try:
        validate_cmmn_json(cmmn_data)
        return []
    except CMMNParseError as e:
        return [str(e)]


def get_schema_info() -> Dict[str, Any]:
    """
    Get information about the CMMN JSON schema.

    Returns:
        Dictionary containing schema metadata
    """
    schema = load_cmmn_schema()
    return {
        "title": schema.get("title", "Unknown"),
        "description": schema.get("description", "No description available"),
        "version": schema.get("$id", "Unknown"),
        "supported_elements": list(schema.get("definitions", {}).keys()),
    }
