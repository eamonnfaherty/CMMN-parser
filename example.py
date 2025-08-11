#!/usr/bin/env python3
"""
Example usage of the CMMN Parser library.
"""

import cmmn_parser
from pathlib import Path


def main():
    # Parse the sample CMMN file
    sample_file = Path("tests/fixtures/sample_cmmn.xml")
    
    print("=== CMMN Parser Example ===\n")
    
    # Parse using convenience function
    definition = cmmn_parser.parse_cmmn_file(sample_file)
    
    # Display basic definition info
    print(f"Target Namespace: {definition.target_namespace}")
    print(f"Expression Language: {definition.expression_language}")
    print(f"Exporter: {definition.exporter} v{definition.exporter_version}")
    print(f"Number of Cases: {len(definition.cases)}\n")
    
    # Iterate through cases
    for case in definition.cases:
        print(f"Case: {case.name} (ID: {case.id})")
        
        # Case roles
        if case.case_roles:
            print(f"  Roles: {', '.join(role.name for role in case.case_roles)}")
        
        # Case file model
        if case.case_file_model:
            print(f"  Case File Items: {len(case.case_file_model.case_file_items)}")
            for item in case.case_file_model.case_file_items:
                print(f"    - {item.name} ({item.definition_type})")
                for child in item.children:
                    print(f"      └─ {child.name}")
        
        # Case plan model
        if case.case_plan_model:
            plan_model = case.case_plan_model
            print(f"  Case Plan: {plan_model.name}")
            print(f"    Auto Complete: {plan_model.auto_complete}")
            print(f"    Plan Items: {len(plan_model.plan_items)}")
            
            # Plan items
            for item in plan_model.plan_items:
                controls = ""
                if item.item_control:
                    ic = item.item_control
                    rules = []
                    if ic.required_rule:
                        rules.append("Required")
                    if ic.repetition_rule:
                        rules.append("Repeatable")
                    if ic.manual_activation_rule:
                        rules.append("Manual")
                    if rules:
                        controls = f" [{', '.join(rules)}]"
                
                print(f"      - {item.name} -> {item.definition_ref}{controls}")
            
            # Task definitions (if available)
            if hasattr(plan_model, '_task_definitions'):
                print(f"    Task Definitions:")
                for task in plan_model._task_definitions:
                    task_info = f"{task.element_type.value}: {task.name}"
                    if hasattr(task, 'performer') and task.performer:
                        task_info += f" (performer: {task.performer})"
                    if hasattr(task, 'process_ref') and task.process_ref:
                        task_info += f" (process: {task.process_ref})"
                    if hasattr(task, 'case_ref') and task.case_ref:
                        task_info += f" (case: {task.case_ref})"
                    print(f"      - {task_info}")
            
            # Event definitions (if available)
            if hasattr(plan_model, '_event_definitions'):
                print(f"    Event Definitions:")
                for event in plan_model._event_definitions:
                    event_info = f"{event.element_type.value}: {event.name}"
                    if hasattr(event, 'timer_expression') and event.timer_expression:
                        event_info += f" (timer: {event.timer_expression})"
                    print(f"      - {event_info}")
            
            # Sentries
            if plan_model.sentries:
                print(f"    Sentries: {len(plan_model.sentries)}")
                for sentry in plan_model.sentries:
                    print(f"      - {sentry.name} (OnParts: {len(sentry.on_parts)}, IfPart: {'Yes' if sentry.if_part else 'No'})")
        
        print()
    
    # Demonstrate helper methods
    print("=== Helper Methods ===")
    specific_case = definition.get_case_by_id("Case_1")
    if specific_case:
        print(f"Found case by ID: {specific_case.name}")
    
    all_plan_items = definition.get_all_plan_items()
    print(f"Total plan items across all cases: {len(all_plan_items)}")
    
    print("\n=== Parsing from String ===")
    
    # Example of parsing from string
    simple_cmmn = '''<?xml version="1.0" encoding="UTF-8"?>
    <cmmn:definitions xmlns:cmmn="http://www.omg.org/spec/CMMN/20151109/MODEL"
                       targetNamespace="http://example.com/simple">
        <cmmn:case id="SimpleCase" name="Simple Example">
            <cmmn:casePlanModel id="SimplePlan" name="Simple Plan">
                <cmmn:planItem id="Item1" name="Simple Task" definitionRef="Task1"/>
                <cmmn:humanTask id="Task1" name="Review Application"/>
            </cmmn:casePlanModel>
        </cmmn:case>
    </cmmn:definitions>'''
    
    simple_def = cmmn_parser.parse_cmmn_string(simple_cmmn)
    simple_case = simple_def.cases[0]
    print(f"Parsed simple case: {simple_case.name}")
    print(f"Plan items: {len(simple_case.case_plan_model.plan_items)}")


if __name__ == "__main__":
    main()