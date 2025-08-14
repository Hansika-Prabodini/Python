#!/usr/bin/env python3
"""
Flake8 Compilation Checker

This script validates Python syntax and compilation errors across the entire project.
It focuses on catching syntax errors, import issues, and basic code structure problems
that would prevent successful compilation.

Usage:
    python scripts/flake8_compilation.py [--fix] [--verbose] [paths...]
    
Examples:
    python scripts/flake8_compilation.py
    python scripts/flake8_compilation.py --verbose data_structures/
    python scripts/flake8_compilation.py --fix sorts/ algorithms/
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def get_python_files(paths: List[str]) -> List[Path]:
    """Get all Python files from the given paths."""
    python_files = []
    
    for path_str in paths:
        path = Path(path_str)
        if path.is_file() and path.suffix == '.py':
            python_files.append(path)
        elif path.is_dir():
            python_files.extend(path.rglob('*.py'))
    
    return sorted(python_files)


def compile_check(file_path: Path) -> tuple[bool, str]:
    """Check if a Python file compiles successfully."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        compile(source, str(file_path), 'exec')
        return True, ""
    except SyntaxError as e:
        return False, f"Syntax Error: {e}"
    except Exception as e:
        return False, f"Compilation Error: {e}"


def run_flake8_compilation_checks(files: List[Path], verbose: bool = False) -> tuple[int, List[str]]:
    """Run flake8 with compilation-focused error codes."""
    if not files:
        return 0, []
    
    # Compilation-focused error codes
    select_codes = [
        'E9',    # Runtime errors (syntax errors, etc.)
        'F63',   # Invalid syntax in docstrings  
        'F7',    # Late binding issues
        'F82',   # Undefined name in __all__
        'F83',   # Duplicate argument in function definition
        'F84',   # Duplicate keyword argument
        'W6',    # Warnings about syntax
        'F401',  # Imported but unused
        'F811',  # Redefined while unused
        'F821',  # Undefined name
        'F822',  # Undefined name in __all__
        'F831',  # Duplicate argument name
        'F841',  # Local variable assigned but never used
    ]
    
    cmd = [
        'flake8',
        '--select=' + ','.join(select_codes),
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


def main():
    """Main function to run compilation checks."""
    parser = argparse.ArgumentParser(
        description='Run flake8 compilation checks on Python files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        'paths',
        nargs='*',
        default=['.'],
        help='Paths to check (default: current directory)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Attempt to fix some issues automatically (limited support)'
    )
    
    parser.add_argument(
        '--exclude',
        default=None,
        help='Comma-separated list of paths to exclude'
    )
    
    args = parser.parse_args()
    
    # Get all Python files from specified paths
    print("🔍 Scanning for Python files...")
    python_files = get_python_files(args.paths)
    
    if not python_files:
        print("No Python files found in the specified paths.")
        return 0
    
    print(f"📁 Found {len(python_files)} Python files")
    
    # First, run basic compilation check
    print("\n🔨 Running compilation checks...")
    compilation_errors = 0
    compilation_issues = []
    
    for file_path in python_files:
        if args.verbose:
            print(f"Checking compilation: {file_path}")
            
        success, error_msg = compile_check(file_path)
        if not success:
            compilation_errors += 1
            compilation_issues.append(f"{file_path}: {error_msg}")
            print(f"❌ {file_path}: {error_msg}")
    
    if compilation_errors == 0:
        print("✅ All files compile successfully")
    else:
        print(f"❌ {compilation_errors} files have compilation errors")
    
    # Run flake8 compilation-focused checks
    print("\n🎯 Running flake8 compilation-focused checks...")
    returncode, flake8_errors = run_flake8_compilation_checks(python_files, args.verbose)
    
    if returncode == 0 and not flake8_errors:
        print("✅ All flake8 compilation checks passed")
    else:
        print(f"❌ Flake8 found {len(flake8_errors)} issues:")
        for error in flake8_errors:
            print(f"  {error}")
    
    # Summary
    total_issues = compilation_errors + len(flake8_errors)
    print(f"\n📊 Summary:")
    print(f"  Files checked: {len(python_files)}")
    print(f"  Compilation errors: {compilation_errors}")
    print(f"  Flake8 issues: {len(flake8_errors)}")
    print(f"  Total issues: {total_issues}")
    
    if total_issues > 0:
        print(f"\n💡 To fix issues:")
        print(f"  1. Address compilation errors first")
        print(f"  2. Run with --verbose for more details")
        print(f"  3. Use your IDE or editor's linting features")
        
        return 1
    else:
        print("\n🎉 All compilation checks passed!")
        return 0


if __name__ == '__main__':
    sys.exit(main())
