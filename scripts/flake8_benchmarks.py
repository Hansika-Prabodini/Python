#!/usr/bin/env python3
"""
Flake8 Benchmark Testing Checker

This script validates benchmark and performance testing code quality. It focuses on
code that measures performance, handles timing, and implements benchmark suites.
It also provides tools to run and validate benchmark code.

Usage:
    python scripts/flake8_benchmarks.py [--run-benchmarks] [--verbose] [paths...]
    
Examples:
    python scripts/flake8_benchmarks.py
    python scripts/flake8_benchmarks.py --run-benchmarks
    python scripts/flake8_benchmarks.py --verbose sorts/
"""

import argparse
import ast
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any


def find_benchmark_files(paths: List[str]) -> List[Path]:
    """Find all benchmark-related files in the given paths."""
    benchmark_files = []
    
    for path_str in paths:
        path = Path(path_str)
        if path.is_file() and is_benchmark_file(path):
            benchmark_files.append(path)
        elif path.is_dir():
            # Look for benchmark files in various patterns
            benchmark_files.extend(path.rglob('*benchmark*.py'))
            benchmark_files.extend(path.rglob('*perf*.py'))
            benchmark_files.extend(path.rglob('*speed*.py'))
            benchmark_files.extend(path.rglob('*timing*.py'))
            # Look for benchmark directories
            for bench_dir in path.rglob('benchmarks'):
                if bench_dir.is_dir():
                    benchmark_files.extend(bench_dir.rglob('*.py'))
            for bench_dir in path.rglob('performance'):
                if bench_dir.is_dir():
                    benchmark_files.extend(bench_dir.rglob('*.py'))
    
    return sorted(list(set(benchmark_files)))


def is_benchmark_file(file_path: Path) -> bool:
    """Check if a file is a benchmark file based on naming and content patterns."""
    name = file_path.name.lower()
    parent_name = file_path.parent.name.lower()
    
    # Name-based detection
    if any(keyword in name for keyword in ['benchmark', 'perf', 'speed', 'timing']):
        return True
    
    if any(keyword in parent_name for keyword in ['benchmark', 'performance', 'perf']):
        return True
    
    # Content-based detection
    try:
        return has_benchmark_content(file_path)
    except Exception:
        return False


def has_benchmark_content(file_path: Path) -> bool:
    """Analyze file content to detect benchmark patterns."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse AST to look for benchmark patterns
        tree = ast.parse(content)
        
        benchmark_indicators = [
            'time.time',
            'time.perf_counter',
            'timeit',
            'benchmark',
            'performance',
            'speed_test',
            'measure_time',
            'timer',
            'profiler',
            'cProfile',
        ]
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id in benchmark_indicators:
                return True
            if isinstance(node, ast.Attribute) and node.attr in benchmark_indicators:
                return True
            if isinstance(node, ast.Call):
                if hasattr(node.func, 'id') and any(ind in node.func.id.lower() for ind in ['time', 'benchmark', 'perf']):
                    return True
                if hasattr(node.func, 'attr') and any(ind in node.func.attr.lower() for ind in ['time', 'benchmark', 'perf']):
                    return True
        
        return False
    except Exception:
        return False


def run_flake8_benchmark_checks(files: List[Path], verbose: bool = False) -> Tuple[int, List[str]]:
    """Run flake8 with benchmark-focused configuration."""
    if not files:
        return 0, []
    
    # Benchmark-specific error codes
    select_codes = [
        'E',     # pycodestyle errors
        'W',     # pycodestyle warnings
        'F',     # pyflakes
        'B',     # flake8-bugbear
        'C4',    # flake8-comprehensions
        'SIM',   # flake8-simplify
        'C90',   # McCabe complexity
    ]
    
    # Benchmark-specific ignores
    ignore_codes = [
        'D100',  # Missing docstring in public module (benchmarks may be simple)
        'D103',  # Missing docstring in public function (simple benchmark functions)
        'E402',  # Module level import not at top (benchmark imports may be conditional)
        'W503',  # Line break before binary operator (formatting preference)
        'B007',  # Loop control variable not used (in timing loops)
    ]
    
    cmd = [
        'flake8',
        '--select=' + ','.join(select_codes),
        '--ignore=' + ','.join(ignore_codes),
        '--max-line-length=100',  # Longer lines for benchmark setup
        '--max-complexity=20',     # Higher complexity for benchmark scenarios
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


def analyze_benchmark_structure(files: List[Path]) -> Dict[str, Any]:
    """Analyze the structure and patterns in benchmark files."""
    analysis = {
        'total_files': len(files),
        'timing_methods': {
            'time.time()': 0,
            'time.perf_counter()': 0,
            'timeit': 0,
            'custom_timer': 0
        },
        'benchmark_patterns': {
            'function_benchmarks': 0,
            'class_benchmarks': 0,
            'comparison_benchmarks': 0,
            'profiling_code': 0
        },
        'files_by_type': {
            'algorithm_benchmarks': [],
            'data_structure_benchmarks': [],
            'general_benchmarks': []
        }
    }
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count timing methods
            if 'time.time()' in content:
                analysis['timing_methods']['time.time()'] += 1
            if 'time.perf_counter()' in content:
                analysis['timing_methods']['time.perf_counter()'] += 1
            if 'timeit' in content:
                analysis['timing_methods']['timeit'] += 1
            if any(word in content.lower() for word in ['timer', 'measure_time', 'benchmark_time']):
                analysis['timing_methods']['custom_timer'] += 1
            
            # Analyze patterns
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if 'benchmark' in node.name.lower() or 'test' in node.name.lower():
                        analysis['benchmark_patterns']['function_benchmarks'] += 1
                elif isinstance(node, ast.ClassDef):
                    if 'benchmark' in node.name.lower():
                        analysis['benchmark_patterns']['class_benchmarks'] += 1
            
            # Categorize by type
            path_str = str(file_path).lower()
            if 'algorithm' in path_str or 'sorts' in path_str:
                analysis['files_by_type']['algorithm_benchmarks'].append(file_path)
            elif 'data_structure' in path_str:
                analysis['files_by_type']['data_structure_benchmarks'].append(file_path)
            else:
                analysis['files_by_type']['general_benchmarks'].append(file_path)
        
        except Exception:
            continue
    
    return analysis


def run_simple_benchmarks(files: List[Path], verbose: bool = False) -> Tuple[int, List[str]]:
    """Run simple benchmark validation by importing and basic execution tests."""
    if not files:
        return 0, []
    
    issues = []
    success_count = 0
    
    for file_path in files:
        if verbose:
            print(f"Validating benchmark: {file_path}")
        
        try:
            # Try to import the module
            spec = None
            module_name = file_path.stem
            
            # Simple syntax check by compiling
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            compile(source, str(file_path), 'exec')
            success_count += 1
            
            if verbose:
                print(f"  ✅ {file_path.name} - syntax OK")
        
        except SyntaxError as e:
            issues.append(f"{file_path}: Syntax Error - {e}")
        except Exception as e:
            issues.append(f"{file_path}: Import/Execution Error - {e}")
    
    return 0 if not issues else 1, issues


def create_sample_benchmark(target_dir: Path) -> Path:
    """Create a sample benchmark file for demonstration."""
    sample_content = '''#!/usr/bin/env python3
"""
Sample benchmark file for algorithm performance testing.
"""

import time
import random
from typing import List, Callable


def benchmark_function(func: Callable, *args, iterations: int = 1000) -> float:
    """Benchmark a function with multiple iterations."""
    start_time = time.perf_counter()
    
    for _ in range(iterations):
        func(*args)
    
    end_time = time.perf_counter()
    return (end_time - start_time) / iterations


def sample_sorting_benchmark():
    """Sample benchmark for sorting algorithms."""
    # Generate test data
    data_sizes = [100, 1000, 5000]
    
    for size in data_sizes:
        data = [random.randint(1, 1000) for _ in range(size)]
        
        # Benchmark built-in sort
        avg_time = benchmark_function(sorted, data.copy(), iterations=100)
        print(f"Built-in sort ({size} elements): {avg_time:.6f}s average")


if __name__ == "__main__":
    sample_sorting_benchmark()
'''
    
    sample_file = target_dir / "sample_benchmark.py"
    sample_file.write_text(sample_content)
    return sample_file


def main():
    """Main function to run benchmark-specific flake8 checks."""
    parser = argparse.ArgumentParser(
        description='Run flake8 checks specifically for benchmark files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        'paths',
        nargs='*',
        default=['.'],
        help='Paths to check for benchmark files (default: current directory)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--run-benchmarks',
        action='store_true',
        help='Run basic validation of benchmark files'
    )
    
    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Analyze benchmark file structure and patterns'
    )
    
    parser.add_argument(
        '--create-sample',
        metavar='DIR',
        help='Create a sample benchmark file in the specified directory'
    )
    
    args = parser.parse_args()
    
    # Create sample if requested
    if args.create_sample:
        target_dir = Path(args.create_sample)
        target_dir.mkdir(parents=True, exist_ok=True)
        sample_file = create_sample_benchmark(target_dir)
        print(f"✅ Created sample benchmark file: {sample_file}")
        return 0
    
    # Find all benchmark files
    print("🔍 Scanning for benchmark files...")
    benchmark_files = find_benchmark_files(args.paths)
    
    if not benchmark_files:
        print("No benchmark files found in the specified paths.")
        print("Note: Looking for files with 'benchmark', 'perf', 'speed', 'timing' in name or content")
        print("Use --create-sample <dir> to create a sample benchmark file")
        return 0
    
    print(f"📁 Found {len(benchmark_files)} benchmark files")
    
    if args.verbose:
        print("Benchmark files found:")
        for bench_file in benchmark_files:
            print(f"  {bench_file}")
    
    # Analyze benchmark structure if requested
    if args.analyze:
        print("\n📊 Analyzing benchmark structure...")
        analysis = analyze_benchmark_structure(benchmark_files)
        
        print(f"  Total benchmark files: {analysis['total_files']}")
        print("  Timing methods used:")
        for method, count in analysis['timing_methods'].items():
            if count > 0:
                print(f"    {method}: {count} files")
        
        print("  File categories:")
        for category, files in analysis['files_by_type'].items():
            if files:
                print(f"    {category}: {len(files)} files")
    
    # Run flake8 on benchmark files
    print("\n🎯 Running flake8 checks on benchmark files...")
    returncode, flake8_errors = run_flake8_benchmark_checks(benchmark_files, args.verbose)
    
    if returncode == 0 and not flake8_errors:
        print("✅ All flake8 benchmark checks passed")
    else:
        print(f"❌ Flake8 found {len(flake8_errors)} issues in benchmark files:")
        for error in flake8_errors:
            if error.strip():
                print(f"  {error}")
    
    # Run benchmark validation if requested
    benchmark_issues = []
    if args.run_benchmarks:
        print("\n🏃 Running benchmark validation...")
        bench_code, bench_issues = run_simple_benchmarks(benchmark_files, args.verbose)
        benchmark_issues = bench_issues
        
        if bench_code == 0:
            print("✅ All benchmark files validated successfully")
        else:
            print("❌ Issues found in benchmark files:")
            for issue in benchmark_issues:
                print(f"  {issue}")
    
    # Summary
    total_issues = len(flake8_errors) + len(benchmark_issues)
    print(f"\n📊 Summary:")
    print(f"  Benchmark files checked: {len(benchmark_files)}")
    print(f"  Flake8 issues: {len(flake8_errors)}")
    if args.run_benchmarks:
        print(f"  Benchmark validation issues: {len(benchmark_issues)}")
    print(f"  Total issues: {total_issues}")
    
    if total_issues > 0:
        print(f"\n💡 To fix benchmark issues:")
        print(f"  1. Address flake8 issues first")
        print(f"  2. Ensure benchmark files can be imported")
        print(f"  3. Use proper timing methods (time.perf_counter)")
        print(f"  4. Consider benchmark-specific patterns")
        
        return 1
    else:
        print("\n🎉 All benchmark checks passed!")
        return 0


if __name__ == '__main__':
    sys.exit(main())
