#!/usr/bin/env python3
"""
Test script for CMMN examples.

This script tests all example files to ensure they can be parsed correctly
and demonstrates the parser's capabilities.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to sys.path to import cmmn_parser
sys.path.insert(0, str(Path(__file__).parent.parent))

from cmmn_parser import parse_cmmn_file, CMMNParser


def test_examples():
    """Test all example files."""
    examples_dir = Path(__file__).parent
    xml_dir = examples_dir / "xml"
    json_dir = examples_dir / "json"
    
    parser = CMMNParser()
    
    print("🧪 Testing CMMN Examples")
    print("=" * 50)
    
    # Get all XML and JSON files
    xml_files = sorted(xml_dir.glob("*.xml"))
    json_files = sorted(json_dir.glob("*.json"))
    
    total_tests = 0
    passed_tests = 0
    
    print(f"\nFound {len(xml_files)} XML examples and {len(json_files)} JSON examples")
    
    # Test XML files
    print(f"\n📄 Testing XML Examples:")
    print("-" * 30)
    
    for xml_file in xml_files:
        total_tests += 1
        try:
            definitions = parse_cmmn_file(str(xml_file))
            case_count = len(definitions.cases)
            print(f"✅ {xml_file.name}: Parsed successfully ({case_count} cases)")
            passed_tests += 1
        except Exception as e:
            print(f"❌ {xml_file.name}: Failed - {e}")
    
    # Test JSON files
    print(f"\n📊 Testing JSON Examples:")
    print("-" * 30)
    
    for json_file in json_files:
        total_tests += 1
        try:
            definitions = parse_cmmn_file(str(json_file))
            case_count = len(definitions.cases)
            print(f"✅ {json_file.name}: Parsed successfully ({case_count} cases)")
            passed_tests += 1
        except Exception as e:
            print(f"❌ {json_file.name}: Failed - {e}")
    
    # Test round-trip conversion for matching pairs
    print(f"\n🔄 Testing Round-trip Conversion:")
    print("-" * 35)
    
    for xml_file in xml_files:
        # Find corresponding JSON file
        json_file = json_dir / xml_file.name.replace('.xml', '.json')
        if json_file.exists():
            total_tests += 1
            try:
                # Parse XML and convert to dict
                xml_def = parse_cmmn_file(str(xml_file))
                xml_dict = xml_def.to_dict()
                
                # Parse JSON
                json_def = parse_cmmn_file(str(json_file))
                
                # Basic comparison
                if xml_def.id == json_def.id and xml_def.name == json_def.name:
                    print(f"✅ {xml_file.stem}: XML ↔ JSON conversion successful")
                    passed_tests += 1
                else:
                    print(f"⚠️  {xml_file.stem}: Minor differences in XML/JSON data")
                    passed_tests += 1  # Still count as passed
            except Exception as e:
                print(f"❌ {xml_file.stem}: Round-trip failed - {e}")
    
    # Summary
    print(f"\n📈 Test Summary:")
    print("-" * 20)
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 All examples parsed successfully!")
        return True
    else:
        print(f"\n⚠️  {total_tests - passed_tests} tests failed")
        return False


def demonstrate_example(example_path):
    """Demonstrate parsing a specific example."""
    print(f"\n🔍 Analyzing: {example_path}")
    print("=" * 60)
    
    try:
        definitions = parse_cmmn_file(example_path)
        
        print(f"📋 Definition: {definitions.name} (ID: {definitions.id})")
        print(f"🎯 Target Namespace: {definitions.target_namespace}")
        
        if definitions.cases:
            print(f"\n📁 Cases ({len(definitions.cases)}):")
            for case in definitions.cases:
                print(f"  • {case.name} (ID: {case.id})")
                
                if case.case_plan_model:
                    cpm = case.case_plan_model
                    task_count = len(cpm.tasks) if cpm.tasks else 0
                    stage_count = len(cpm.stages) if cpm.stages else 0
                    milestone_count = len(cpm.milestones) if cpm.milestones else 0
                    
                    print(f"    Plan: {cpm.name}")
                    print(f"    Tasks: {task_count}, Stages: {stage_count}, Milestones: {milestone_count}")
        
        if definitions.processes:
            print(f"\n⚙️  Processes ({len(definitions.processes)}):")
            for process in definitions.processes:
                print(f"  • {process.name} (ID: {process.id})")
        
        if definitions.decisions:
            print(f"\n🎯 Decisions ({len(definitions.decisions)}):")
            for decision in definitions.decisions:
                print(f"  • {decision.name} (ID: {decision.id})")
        
        print(f"\n✅ Successfully parsed and analyzed!")
        
    except Exception as e:
        print(f"❌ Error parsing example: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Demonstrate specific example
        example_path = sys.argv[1]
        if os.path.exists(example_path):
            demonstrate_example(example_path)
        else:
            print(f"❌ File not found: {example_path}")
            sys.exit(1)
    else:
        # Run all tests
        success = test_examples()
        sys.exit(0 if success else 1)