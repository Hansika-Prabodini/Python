#!/usr/bin/env python3
"""
Flake8 Unit Test Checker

This script validates unit test code quality and ensures proper testing practices
across the project. It focuses on test-specific linting rules and validates that
test files follow proper conventions.

Usage:
    python scripts/flake8_tests.py [--run-tests] [--verbose] [paths...]
    
Examples:
    python scripts/flake8_tests.py
    python scripts/flake8_tests.py --run-tests
    python scripts/flake8_tests.py --verbose data_structures/hashing/tests/
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple


def find_test_files(paths: List[str]) -> List[Path]:
    """Find all test files in the given paths."""
    test_files = []
    
    for path_str in paths:
        path = Path(path_str)
        if path.is_file() and is_test_file(path):
            test_files.append(path)
        elif path.is_dir():
            # Look for test files in various patterns
            test_files.extend(path.rglob('test_*.py'))
            test_files.extend(path.rglob('*_test.py'))
            test_files.extend(path.rglob('tests.py'))
            # Also check for tests/ directories
            for test_dir in path.rglob('tests'):
                if test_dir.is_dir():
                    test_files.extend(test_dir.rglob('*.py'))
    
    return sorted(list(set(test_files)))


def is_test_file(file_path: Path) -> bool:
    """Check if a file is a test file based on naming conventions."""
    name = file_path.name
    parent_name = file_path.parent.name
    
    return (
        name.startswith('test_') or
        name.endswith('_test.py') or
        name == 'tests.py' or
        parent_name == 'tests' or
        'test' in name.lower()
    )


def run_flake8_test_checks(files: List[Path], verbose: bool = False) -> Tuple[int, List[str]]:
    """Run flake8 with test-focused configuration."""
    if not files:
        return 0, []
    
    # Test-specific error codes to focus on
    select_codes = [
        'E',     # pycodestyle errors
        'W',     # pycodestyle warnings
        'F',     # pyflakes
        'B',     # flake8-bugbear
        'C4',    # flake8-comprehensions
        'D',     # flake8-docstrings (relaxed for tests)
        'SIM',   # flake8-simplify
    ]
    
    # Test-specific ignores
    ignore_codes = [
        'D100',  # Missing docstring in public module (tests don't always need module docstrings)
        'D101',  # Missing docstring in public class (test classes)
        'D102',  # Missing docstring in public method (test methods)
        'D103',  # Missing docstring in public function (test functions)
        'D104',  # Missing docstring in public package
        'S101',  # Use of assert (allowed in tests)
        'S105',  # Possible hardcoded password (common in test fixtures)
        'S106',  # Possible hardcoded password (common in test fixtures)
        'B011',  # assert False (common in negative tests)
    ]
    
    cmd = [
        'flake8',
        '--select=' + ','.join(select_codes),
        '--ignore=' + ','.join(ignore_codes),
        '--max-line-length=100',  # Slightly longer lines for test setup
        '--max-complexity=15',     # Slightly higher complexity for test setup
        '--show-source',
        '--statistics',
    ] + [str(f) for f in files]
    
    if verbose:
        print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=False
        )
        
        errors = []
        if result.stdout:
            errors.extend(result.stdout.strip().split('\n'))
        if result.stderr:
            errors.extend(result.stderr.strip().split('\n'))
            
        return result.returncode, [e for e in errors if e.strip()]
    
    except FileNotFoundError:
        print("Error: flake8 not found. Please install it with: pip install flake8")
        return 1, ["flake8 not found"]


def run_pytest_collection(test_files: List[Path], verbose: bool = False) -> Tuple[int, List[str]]:
    """Run pytest collection to validate test structure."""
    if not test_files:
        return 0, []
    
    # Get unique directories containing test files
    test_dirs = list(set(f.parent for f in test_files))
    
    cmd = ['python', '-m', 'pytest', '--collect-only', '-q'] + [str(d) for d in test_dirs]
    
    if verbose:
        print(f"Running pytest collection: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            cwd=Path.cwd()
        )
        
        output_lines = []
        if result.stdout:
            output_lines.extend(result.stdout.strip().split('\n'))
        if result.stderr:
            output_lines.extend(result.stderr.strip().split('\n'))
        
        return result.returncode, [line for line in output_lines if line.strip()]
    
    except FileNotFoundError:
        print("Warning: pytest not found. Skipping test collection validation.")
        return 0, ["pytest not available"]


def analyze_test_coverage(test_files: List[Path]) -> dict:
    """Analyze test file structure and coverage patterns."""
    analysis = {
        'total_test_files': len(test_files),
        'test_directories': set(),
        'test_patterns': {
            'test_*.py': 0,
            '*_test.py': 0,
            'tests.py': 0,
            'tests/ directory': 0
        },
        'files_by_directory': {}
    }
    
    for test_file in test_files:
        # Track directories
        analysis['test_directories'].add(test_file.parent)
        
        # Count patterns
        name = test_file.name
        if name.startswith('test_'):
            analysis['test_patterns']['test_*.py'] += 1
        elif name.endswith('_test.py'):
            analysis['test_patterns']['*_test.py'] += 1
        elif name == 'tests.py':
            analysis['test_patterns']['tests.py'] += 1
        elif test_file.parent.name == 'tests':
            analysis['test_patterns']['tests/ directory'] += 1
        
        # Files by directory
        dir_name = str(test_file.parent)
        if dir_name not in analysis['files_by_directory']:
            analysis['files_by_directory'][dir_name] = []
        analysis['files_by_directory'][dir_name].append(test_file.name)
    
    return analysis


def main():
    """Main function to run test-specific flake8 checks."""
    parser = argparse.ArgumentParser(
        description='Run flake8 checks specifically for unit test files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        'paths',
        nargs='*',
        default=['.'],
        help='Paths to check for test files (default: current directory)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--run-tests',
        action='store_true',
        help='Also run pytest collection to validate test structure'
    )
    
    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Analyze test file structure and patterns'
    )
    
    args = parser.parse_args()
    
    # Find all test files
    print("🔍 Scanning for test files...")
    test_files = find_test_files(args.paths)
    
    if not test_files:
        print("No test files found in the specified paths.")
        print("Note: Looking for files matching: test_*.py, *_test.py, tests.py, or files in tests/ directories")
        return 0
    
    print(f"📁 Found {len(test_files)} test files")
    
    if args.verbose:
        print("Test files found:")
        for test_file in test_files:
            print(f"  {test_file}")
    
    # Analyze test structure if requested
    if args.analyze:
        print("\n📊 Analyzing test structure...")
        analysis = analyze_test_coverage(test_files)
        
        print(f"  Total test files: {analysis['total_test_files']}")
        print(f"  Test directories: {len(analysis['test_directories'])}")
        print("  Pattern breakdown:")
        for pattern, count in analysis['test_patterns'].items():
            if count > 0:
                print(f"    {pattern}: {count} files")
    
    # Run flake8 on test files
    print("\n🎯 Running flake8 checks on test files...")
    returncode, flake8_errors = run_flake8_test_checks(test_files, args.verbose)
    
    if returncode == 0 and not flake8_errors:
        print("✅ All flake8 test checks passed")
    else:
        print(f"❌ Flake8 found {len(flake8_errors)} issues in test files:")
        for error in flake8_errors:
            if error.strip():
                print(f"  {error}")
    
    # Run pytest collection if requested
    pytest_issues = []
    if args.run_tests:
        print("\n🧪 Running pytest collection validation...")
        pytest_code, pytest_output = run_pytest_collection(test_files, args.verbose)
        
        if pytest_code == 0:
            print("✅ All tests can be collected successfully")
            if args.verbose and pytest_output:
                for line in pytest_output:
                    if 'collected' in line.lower():
                        print(f"  {line}")
        else:
            print("❌ Issues found during test collection:")
            pytest_issues = pytest_output
            for issue in pytest_issues:
                if issue.strip():
                    print(f"  {issue}")
    
    # Summary
    total_issues = len(flake8_errors) + len(pytest_issues)
    print(f"\n📊 Summary:")
    print(f"  Test files checked: {len(test_files)}")
    print(f"  Flake8 issues: {len(flake8_errors)}")
    if args.run_tests:
        print(f"  Pytest collection issues: {len(pytest_issues)}")
    print(f"  Total issues: {total_issues}")
    
    if total_issues > 0:
        print(f"\n💡 To fix test issues:")
        print(f"  1. Address flake8 issues first")
        print(f"  2. Run individual tests to debug collection issues")
        print(f"  3. Use --verbose for more details")
        print(f"  4. Consider test-specific coding standards")
        
        return 1
    else:
        print("\n🎉 All test checks passed!")
        return 0


if __name__ == '__main__':
    sys.exit(main())
