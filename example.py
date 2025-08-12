#!/usr/bin/env python3
"""
Example usage of the CMMN Parser library.

This example demonstrates how to use the CMMN parser to parse both XML and JSON
CMMN files, and how to work with the parsed data structures.
"""

import json
import cmmn_parser
from cmmn_parser import CMMNParser


def main():
    print("=== CMMN Parser Example ===\n")
    
    # Example 1: Parse XML from string
    print("1. Parsing XML from string:")
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/CMMN/20151109/MODEL"
             id="demo_case" 
             name="Demo Case Management"
             targetNamespace="http://demo.example.com/cmmn"
             exporter="Demo Modeler" 
             exporterVersion="1.0">
    
    <caseFileItemDefinition id="customer_data" 
                           name="Customer Data" 
                           structureRef="Customer">
        <definitiveProperty name="customerId"/>
    </caseFileItemDefinition>
    
    <case id="customer_case" name="Customer Management">
        <casePlanModel id="main_plan" name="Main Plan" autoComplete="false">
            <planItem id="pi_review" 
                     name="Review Process" 
                     definitionRef="review_task">
                <entryCriterion sentryRef="start_sentry"/>
            </planItem>
            
            <sentry id="start_sentry" name="Start Condition">
                <planItemOnPart sourceRef="data_collection"/>
                <ifPart>customer_data.customerId != null</ifPart>
            </sentry>
            
            <humanTask id="review_task" 
                      name="Review Customer Data" 
                      performer="agent"
                      isBlocking="true"/>
            
            <milestone id="process_complete" 
                      name="Process Complete"/>
        </casePlanModel>
    </case>
    
    <process id="validation_process" 
            name="Data Validation Process" 
            isExecutable="true"/>
</definitions>'''
    
    # Parse using convenience function
    definitions = cmmn_parser.parse_cmmn_string(xml_content)
    
    # Display basic definition info
    print(f"  ID: {definitions.id}")
    print(f"  Name: {definitions.name}")
    print(f"  Target Namespace: {definitions.target_namespace}")
    print(f"  Exporter: {definitions.exporter} v{definitions.exporter_version}")
    print(f"  Number of Cases: {len(definitions.cases)}")
    print(f"  Number of Processes: {len(definitions.processes)}")
    print(f"  Case File Item Definitions: {len(definitions.case_file_item_definitions)}")
    print()
    
    # Iterate through cases
    for case in definitions.cases:
        print(f"  Case: {case.name} (ID: {case.id})")
        
        # Case plan model
        if case.case_plan_model:
            plan_model = case.case_plan_model
            print(f"    Case Plan: {plan_model.name}")
            print(f"    Auto Complete: {plan_model.auto_complete}")
            print(f"    Plan Items: {len(plan_model.plan_items)}")
            print(f"    Tasks: {len(plan_model.tasks)}")
            print(f"    Sentries: {len(plan_model.sentries)}")
            print(f"    Milestones: {len(plan_model.milestones)}")
            
            # Show tasks
            for task in plan_model.tasks:
                task_type = type(task).__name__
                print(f"      Task: {task.name} (Type: {task_type}, ID: {task.id})")
                if hasattr(task, 'performer') and task.performer:
                    print(f"        Performer: {task.performer}")
    print()
    
    # Example 2: Convert to JSON and parse back
    print("2. Converting to JSON and parsing back:")
    
    # Convert parsed definitions to dictionary
    data_dict = definitions.to_dict()
    
    # Convert to JSON string
    json_content = json.dumps(data_dict, indent=2)
    print(f"  JSON representation created ({len(json_content)} characters)")
    
    # Parse JSON back
    json_definitions = cmmn_parser.parse_cmmn_string(json_content)
    
    # Verify round-trip
    print(f"  Round-trip successful:")
    print(f"    Original ID: {definitions.id}")
    print(f"    Parsed ID: {json_definitions.id}")
    print(f"    Cases match: {len(definitions.cases) == len(json_definitions.cases)}")
    print()
    
    # Example 3: Using the parser directly
    print("3. Using CMMNParser directly:")
    
    parser = CMMNParser()
    
    # Parse with explicit format
    xml_result = parser.parse_xml_string(xml_content)
    json_result = parser.parse_json_string(json_content)
    
    print(f"  XML parse result ID: {xml_result.id}")
    print(f"  JSON parse result ID: {json_result.id}")
    
    # Format detection
    print(f"  Auto-detected XML format: {parser._detect_format(xml_content, 'auto')}")
    print(f"  Auto-detected JSON format: {parser._detect_format(json_content, 'auto')}")
    print()
    
    # Example 4: Error handling
    print("4. Error handling:")
    
    try:
        invalid_xml = "<invalid><unclosed>"
        cmmn_parser.parse_cmmn_string(invalid_xml)
    except cmmn_parser.CMMNParsingError as e:
        print(f"  Caught parsing error: {e}")
    
    try:
        invalid_json = '{"invalid": json}'
        cmmn_parser.parse_cmmn_string(invalid_json)
    except cmmn_parser.CMMNParsingError as e:
        print(f"  Caught JSON error: {e}")
    print()
    
    # Example 5: Working with complex structures
    print("5. Working with complex structures:")
    
    case = definitions.cases[0]
    if case.case_plan_model:
        cpm = case.case_plan_model
        
        # Find specific elements
        sentries = [s for s in cpm.sentries if s.if_part]
        print(f"  Sentries with conditions: {len(sentries)}")
        
        for sentry in sentries:
            print(f"    {sentry.name}: {sentry.if_part}")
        
        # Task analysis
        from cmmn_parser.models import HumanTask, ProcessTask
        human_tasks = [t for t in cpm.tasks if isinstance(t, HumanTask)]
        process_tasks = [t for t in cpm.tasks if isinstance(t, ProcessTask)]
        
        print(f"  Human tasks: {len(human_tasks)}")
        print(f"  Process tasks: {len(process_tasks)}")
        
        for task in human_tasks:
            print(f"    Human task: {task.name} (Performer: {task.performer})")
    
    print("\n=== Example Complete ===")


if __name__ == "__main__":
    main()