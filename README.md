# CMMN Parser

[![CI](https://github.com/eamonnfaherty/CMMN-parser/workflows/CI/badge.svg)](https://github.com/eamonnfaherty/CMMN-parser/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/eamonnfaherty/CMMN-parser/branch/main/graph/badge.svg)](https://codecov.io/gh/eamonnfaherty/CMMN-parser)
[![PyPI version](https://badge.fury.io/py/CMMN-parser.svg)](https://badge.fury.io/py/CMMN-parser)
[![Python versions](https://img.shields.io/pypi/pyversions/CMMN-parser.svg)](https://pypi.org/project/CMMN-parser/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python library for parsing CMMN (Case Management Model and Notation) files in both XML and JSON formats. This library provides a complete, typed interface for working with CMMN documents, supporting all major CMMN constructs including stages, tasks, events, milestones, sentries, and case file items.

## Features

- **Complete CMMN Support**: Parse all CMMN 1.1 constructs including:
  - Cases and Case Plan Models
  - Stages (including nested stages)
  - Tasks (Human, Process, Case tasks)
  - Events (Timer, User events)
  - Milestones and Sentries
  - Case File Items with hierarchies
  - Entry/Exit/Reactivation Criteria
  - Plan Items with Item Controls

- **Multiple Format Support**: 
  - **XML Format**: Traditional CMMN XML files
  - **JSON Format**: Modern JSON representation with full schema validation
  - **Auto-Detection**: Automatically detects file format based on content

- **JSON Schema Validation**: Built-in JSONSchema validation for CMMN JSON files
- **Type Safety**: Fully typed with comprehensive dataclasses for all CMMN elements
- **Flexible Input**: Parse from files or strings in either format
- **Validation Functions**: Standalone validation functions for JSON format
- **Error Handling**: Comprehensive error handling with detailed error messages
- **High Test Coverage**: 98% test coverage with exhaustive unit tests
- **Python 3.8+ Support**: Compatible with Python 3.8 through 3.13

## Installation

```bash
pip install CMMN-parser
```

Or using uv:
```bash
uv add CMMN-parser
```

## Quick Start

### Parse from File (Auto-Detection)

```python
import cmmn_parser

# Parse a CMMN file (XML or JSON - auto-detected)
definition = cmmn_parser.parse_cmmn_file("path/to/your/case.cmmn")  # or .json

# Access cases
for case in definition.cases:
    print(f"Case: {case.name}")
    
    # Access case plan model
    if case.case_plan_model:
        print(f"  Plan Items: {len(case.case_plan_model.plan_items)}")
        for item in case.case_plan_model.plan_items:
            print(f"    - {item.name}")
```

### Parse from String

```python
import cmmn_parser

cmmn_xml = """<?xml version="1.0" encoding="UTF-8"?>
<cmmn:definitions xmlns:cmmn="http://www.omg.org/spec/CMMN/20151109/MODEL">
    <cmmn:case id="SimpleCase" name="Simple Case">
        <cmmn:casePlanModel id="CasePlan" name="Case Plan">
            <cmmn:planItem id="Task1" name="Review" definitionRef="HumanTask1"/>
            <cmmn:humanTask id="HumanTask1" name="Review Document"/>
        </cmmn:casePlanModel>
    </cmmn:case>
</cmmn:definitions>"""

definition = cmmn_parser.parse_cmmn_string(cmmn_xml)
case = definition.cases[0]
print(f"Parsed case: {case.name}")
```

### Using the Parser Class Directly

```python
from cmmn_parser import CMMNParser

parser = CMMNParser()

# Parse file
definition = parser.parse_file("case.cmmn")

# Parse string
definition = parser.parse_string(cmmn_xml_string)
```

## JSON Format Support

### Parse from JSON String

```python
import cmmn_parser

cmmn_json = {
    "definitions": {
        "targetNamespace": "http://example.com/cmmn",
        "cases": [
            {
                "id": "SimpleCase",
                "name": "Simple Case",
                "casePlanModel": {
                    "id": "CasePlan",
                    "name": "Case Plan",
                    "planItems": [
                        {
                            "id": "Task1",
                            "name": "Review",
                            "definitionRef": "HumanTask1"
                        }
                    ],
                    "taskDefinitions": [
                        {
                            "id": "HumanTask1",
                            "name": "Review Document",
                            "performer": "reviewer"
                        }
                    ]
                }
            }
        ]
    }
}

# Parse from dictionary
definition = cmmn_parser.parse_cmmn_json(cmmn_json)

# Or parse from JSON string
import json
definition = cmmn_parser.parse_cmmn_json(json.dumps(cmmn_json))

case = definition.cases[0]
print(f"Parsed case: {case.name}")
```

### Parse from JSON File

```python
import cmmn_parser

# Parse JSON file directly
definition = cmmn_parser.parse_cmmn_json_file("case.json")

# Or use the generic function (auto-detects format)
definition = cmmn_parser.parse_cmmn_file("case.json")
```

### JSON Validation

```python
import cmmn_parser

# Validate JSON data
cmmn_json = {
    "definitions": {
        "cases": [
            {
                "id": "TestCase",
                "name": "Test Case"
            }
        ]
    }
}

# Validate and get boolean result
try:
    is_valid = cmmn_parser.validate_cmmn_json(cmmn_json)
    print("JSON is valid!")
except cmmn_parser.CMMNParseError as e:
    print(f"Validation failed: {e}")

# Get validation errors without exception
errors = cmmn_parser.get_validation_errors(cmmn_json)
if errors:
    print("Validation errors:", errors)
else:
    print("No validation errors")

# Validate JSON file
try:
    is_valid = cmmn_parser.validate_cmmn_json_file("case.json")
    print("File is valid!")
except cmmn_parser.CMMNParseError as e:
    print(f"File validation failed: {e}")

# Get schema information
schema_info = cmmn_parser.get_schema_info()
print(f"Schema: {schema_info['title']}")
print(f"Supported elements: {len(schema_info['supported_elements'])}")
```

## Advanced Usage

### Working with Complex CMMN Structures

```python
import cmmn_parser

definition = cmmn_parser.parse_cmmn_file("complex_case.cmmn")

for case in definition.cases:
    print(f"Case: {case.name}")
    
    # Case file items
    if case.case_file_model:
        for item in case.case_file_model.case_file_items:
            print(f"  Case File Item: {item.name}")
            for child in item.children:
                print(f"    Child: {child.name}")
    
    # Case plan model details
    if case.case_plan_model:
        plan = case.case_plan_model
        
        # Plan items with controls
        for plan_item in plan.plan_items:
            controls = []
            if plan_item.item_control:
                if plan_item.item_control.required_rule:
                    controls.append("Required")
                if plan_item.item_control.repetition_rule:
                    controls.append("Repeatable")
            
            control_str = f" [{', '.join(controls)}]" if controls else ""
            print(f"    Plan Item: {plan_item.name}{control_str}")
        
        # Sentries
        for sentry in plan.sentries:
            print(f"    Sentry: {sentry.name}")
            print(f"      On Parts: {len(sentry.on_parts)}")
            print(f"      If Part: {'Yes' if sentry.if_part else 'No'}")
```

### Helper Methods

```python
# Find specific case by ID
case = definition.get_case_by_id("MyCase")

# Get all plan items across all cases
all_plan_items = definition.get_all_plan_items()
print(f"Total plan items: {len(all_plan_items)}")
```

### Error Handling

```python
from cmmn_parser import CMMNParseError

try:
    definition = cmmn_parser.parse_cmmn_file("invalid_file.cmmn")
except CMMNParseError as e:
    print(f"Failed to parse CMMN: {e}")
```

## CMMN Elements Supported

| Element Type | Class | Description |
|--------------|-------|-------------|
| Case | `Case` | Root case element |
| Case Plan Model | `CasePlanModel` | Main case plan |
| Stage | `Stage` | Planning containers |
| Human Task | `HumanTask` | Tasks performed by humans |
| Process Task | `ProcessTask` | Automated process tasks |
| Case Task | `CaseTask` | Tasks that invoke sub-cases |
| Milestone | `Milestone` | Achievement markers |
| Timer Event | `TimerEventListener` | Time-based events |
| User Event | `UserEventListener` | User-triggered events |
| Sentry | `Sentry` | Condition-based guards |
| Case File Item | `CaseFileItem` | Data elements |
| Plan Item | `PlanItem` | Planned work items |

## Development

### Prerequisites

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Setup

```bash
# Clone the repository
git clone https://github.com/eamonnfaherty/CMMN-parser.git
cd CMMN-parser

# Install development dependencies
make install-dev

# See all available commands
make help
```

### Available Make Commands

```bash
# Development workflow
make install-dev     # Install development dependencies  
make test           # Run tests
make test-cov       # Run tests with coverage report
make lint           # Run linting (flake8)
make format         # Format code (black + isort)
make type-check     # Run type checking (mypy)

# CI commands (same as GitHub Actions)
make ci             # Run full CI suite
make pr-check       # Quick PR validation checks
make security       # Run security checks

# Build and release
make build          # Build package
make clean          # Clean build artifacts
make pre-release    # Full pre-release validation
```

### Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run specific test file (using uv directly)
uv run pytest tests/test_parser.py -v
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `make ci`
5. Submit a pull request

Please ensure:
- All tests pass: `make test`
- Code coverage remains high (>95%): `make test-cov`
- Code is formatted: `make format`
- Type checking passes: `make type-check`
- Linting passes: `make lint`
- Documentation is updated as needed

**Quick validation before submitting:** `make pr-check`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a history of changes.

## Support

- Documentation: [GitHub Wiki](https://github.com/eamonnfaherty/CMMN-parser/wiki)
- Issues: [GitHub Issues](https://github.com/eamonnfaherty/CMMN-parser/issues)
- Discussions: [GitHub Discussions](https://github.com/eamonnfaherty/CMMN-parser/discussions)