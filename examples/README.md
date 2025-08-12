# CMMN Parser Examples

This directory contains a comprehensive collection of CMMN (Case Management Model and Notation) examples demonstrating various features and capabilities of the CMMN specification. Each example is provided in both XML and JSON formats to showcase the parser's dual-format support.

## Directory Structure

```
examples/
├── xml/           # CMMN examples in XML format
├── json/          # Corresponding examples in JSON format  
└── README.md      # This file
```

## Example Files Overview

| File | XML | JSON | Description |
|------|-----|------|-------------|
| **01-basic-case** | ✓ | ✓ | Simple case with a single task |
| **02-human-tasks** | ✓ | ✓ | Multiple human tasks with performers |
| **03-process-tasks** | ✓ | ✓ | Process tasks referencing external processes |
| **04-stages-and-milestones** | ✓ | ✓ | Hierarchical stages with milestones |
| **05-sentries-and-criteria** | ✓ | ✓ | Entry/exit criteria with conditional logic |
| **06-case-file-items** | ✓ | ✓ | Case file management and data structures |
| **07-decision-tasks** | ✓ | ✓ | Decision tasks with business logic |
| **08-complex-example** | ✓ | ✓ | Comprehensive example with all features |

## Getting Started

### Using the Examples with the Parser

```python
from cmmn_parser import parse_cmmn_file, parse_cmmn_string

# Parse an XML example
definitions = parse_cmmn_file('examples/xml/01-basic-case.xml')
print(f"Loaded case: {definitions.cases[0].name}")

# Parse a JSON example  
definitions = parse_cmmn_file('examples/json/01-basic-case.json')
print(f"Loaded case: {definitions.cases[0].name}")

# Convert between formats
xml_definitions = parse_cmmn_file('examples/xml/08-complex-example.xml')
json_dict = xml_definitions.to_dict()
```

### Running Examples

You can test any example file using the main example script:

```bash
# Test XML parsing
python example.py examples/xml/04-stages-and-milestones.xml

# Test JSON parsing  
python example.py examples/json/07-decision-tasks.json
```

## Example Descriptions

### 1. Basic Case (`01-basic-case`)
**Demonstrates:** Minimal CMMN structure
- Single case definition
- One simple task
- Basic case plan model

**Key Elements:**
- `<definitions>` root element
- `<case>` with `<casePlanModel>`
- Simple `<task>` element

### 2. Human Tasks (`02-human-tasks`)
**Demonstrates:** Human task assignments
- Multiple human tasks
- Task performers/assignees
- Blocking vs. non-blocking tasks

**Key Elements:**
- `<humanTask>` elements
- `performer` attribute
- `isBlocking` property

### 3. Process Tasks (`03-process-tasks`)
**Demonstrates:** External process integration
- Process definitions
- Process task references
- Executable processes

**Key Elements:**
- `<process>` definitions
- `<processTask>` with `processRef`
- `isExecutable` attribute

### 4. Stages and Milestones (`04-stages-and-milestones`)
**Demonstrates:** Hierarchical case structure
- Nested stages
- Plan items within stages
- Milestone definitions

**Key Elements:**
- `<stage>` elements with nested tasks
- `<planItem>` definitions
- `<milestone>` elements
- `autoComplete` behavior

### 5. Sentries and Criteria (`05-sentries-and-criteria`)
**Demonstrates:** Conditional execution logic
- Entry criteria for tasks
- Sentry definitions
- Conditional expressions
- Event-based triggers

**Key Elements:**
- `<sentry>` definitions
- `<planItemOnPart>` for events
- `<ifPart>` for conditions
- `entryCriteriaRefs` attributes

### 6. Case File Items (`06-case-file-items`)
**Demonstrates:** Data management
- Case file item definitions
- Data structure references
- Definitive properties
- Case file model

**Key Elements:**
- `<caseFileItemDefinition>`
- `<caseFileModel>`
- `<caseFileItem>` elements
- `definitiveProperty` lists

### 7. Decision Tasks (`07-decision-tasks`)
**Demonstrates:** Automated decision making
- Decision definitions
- Decision task execution  
- Business rule logic
- Conditional branching

**Key Elements:**
- `<decision>` definitions
- `<decisionTask>` with `decisionRef`
- `<decisionLogic>` expressions
- Rule-based sentries

### 8. Complex Example (`08-complex-example`)
**Demonstrates:** Real-world healthcare case
- Multiple integrated stages
- All CMMN element types
- Complex workflow logic
- Extension elements
- Import statements

**Key Elements:**
- Comprehensive metadata
- Multi-stage patient care workflow
- Emergency response handling
- Extension elements for customization
- All task types (human, process, decision)

## CMMN Elements Coverage

| Element Type | Examples |
|--------------|----------|
| **Basic Structure** | |
| Definitions | All examples |
| Cases | All examples |
| Case Plan Models | All examples |
| **Tasks** | |
| Task | 01, 05 |
| Human Task | 02, 04, 05, 06, 07, 08 |
| Process Task | 03, 06, 08 |
| Decision Task | 07, 08 |
| Case Task | - |
| **Structure** | |
| Stages | 04, 08 |
| Plan Items | 04, 05, 08 |
| Milestones | 04, 08 |
| **Control Flow** | |
| Sentries | 05, 07, 08 |
| Entry Criteria | 05, 07, 08 |
| Exit Criteria | - |
| **Data** | |
| Case File Items | 06, 08 |
| Case File Item Definitions | 06, 08 |
| **Extensions** | |
| Extension Elements | 08 |
| Imports | 08 |
| Processes | 03, 08 |
| Decisions | 07, 08 |

## Use Cases by Domain

### Business Process Management
- **Order Processing**: Examples 05, 07 (conditional workflows)
- **Document Review**: Example 02 (approval workflows)
- **Customer Onboarding**: Example 06 (data collection)

### Healthcare
- **Patient Care**: Example 08 (comprehensive care management)
- **Emergency Response**: Example 08 (conditional emergency handling)

### Insurance
- **Claim Processing**: Example 04 (multi-stage assessment)
- **Application Processing**: Examples 01, 07 (approval workflows)

### Financial Services  
- **Loan Processing**: Examples 03, 07 (credit decisions)
- **Risk Assessment**: Example 07 (decision logic)

## Testing the Examples

### Validation Testing
```python
from cmmn_parser import CMMNParser

parser = CMMNParser()

# Test XML validation
parser.validate_xml_file('examples/xml/08-complex-example.xml')

# Test JSON validation  
parser.validate_json_file('examples/json/08-complex-example.json')
```

### Round-trip Testing
```python
# Parse XML, convert to JSON, and parse back
xml_def = parse_cmmn_file('examples/xml/01-basic-case.xml')
json_dict = xml_def.to_dict()

# Verify data integrity
assert xml_def.id == json_dict['id']
assert xml_def.name == json_dict['name']
```

## Extending the Examples

### Adding Custom Examples
1. Create XML file in `examples/xml/`
2. Create corresponding JSON in `examples/json/`
3. Test with the parser
4. Update this README

### Best Practices
- Use descriptive IDs and names
- Include documentation elements
- Validate against the schema
- Test both XML and JSON versions
- Follow CMMN 1.1 specification

## Schema Compliance

All examples are designed to be compliant with:
- **CMMN 1.1 Specification**
- **XSD Schema** (located in `references/` directory)
- **JSON Schema** (defined in parser validation)

## Troubleshooting

### Common Issues
1. **Validation Errors**: Check element structure against CMMN spec
2. **Reference Errors**: Ensure all `*Ref` attributes point to existing elements
3. **Namespace Issues**: Verify correct CMMN namespace usage

### Getting Help
- Review the CMMN 1.1 specification
- Check parser documentation
- Examine working examples for patterns
- Use parser validation methods for debugging

---

*These examples demonstrate the rich capabilities of CMMN for case management and provide a foundation for building your own case models.*