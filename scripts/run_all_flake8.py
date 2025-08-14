#!/usr/bin/env python3
"""
Run All Flake8 Checks

This script orchestrates all three types of flake8 checks:
1. Compilation checks (syntax and import errors)
2. Unit test checks (test code quality)
3. Benchmark checks (performance code quality)

Usage:
    python scripts/run_all_flake8.py [options] [paths...]
    
Examples:
    python scripts/run_all_flake8.py
    python scripts/run_all_flake8.py --verbose
    python scripts/run_all_flake8.py --skip-tests data_structures/
    python scripts/run_all_flake8.py --only compilation
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Dict, Tuple


def run_script(script_name: str, args: List[str], verbose: bool = False) -> Tuple[int, str, str]:
    """Run a flake8 script and return the result."""
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        return 1, "", f"Script not found: {script_path}"
    
    cmd = [sys.executable, str(script_path)] + args
    
    if verbose:
        print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        return result.returncode, result.stdout, result.stderr
    
    except Exception as e:
        return 1, "", f"Error running {script_name}: {e}"


def format_duration(seconds: float) -> str:
    """Format duration in a human-readable way."""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"


def print_section_header(title: str, icon: str = "🔍"):
    """Print a formatted section header."""
    print(f"\n{icon} {title}")
    print("=" * (len(title) + 3))


def print_results_summary(results: Dict[str, Dict]):
    """Print a comprehensive summary of all results."""
    print_section_header("📊 COMPREHENSIVE SUMMARY", "📊")
    
    total_checks = len(results)
    passed_checks = sum(1 for r in results.values() if r['returncode'] == 0)
    failed_checks = total_checks - passed_checks
    total_time = sum(r['duration'] for r in results.values())
    
    print(f"Total checks run: {total_checks}")
    print(f"Passed: {passed_checks} ✅")
    print(f"Failed: {failed_checks} ❌")
    print(f"Total time: {format_duration(total_time)}")
    
    print("\nDetailed Results:")
    for check_name, result in results.items():
        status = "✅ PASS" if result['returncode'] == 0 else "❌ FAIL"
        duration = format_duration(result['duration'])
        print(f"  {check_name}: {status} ({duration})")
    
    if failed_checks > 0:
        print(f"\n🔧 Failed Checks Details:")
        for check_name, result in results.items():
            if result['returncode'] != 0:
                print(f"\n{check_name}:")
                if result['stdout']:
                    print("  STDOUT:")
                    for line in result['stdout'].split('\n'):
                        if line.strip():
                            print(f"    {line}")
                if result['stderr']:
                    print("  STDERR:")
                    for line in result['stderr'].split('\n'):
                        if line.strip():
                            print(f"    {line}")


def main():
    """Main function to orchestrate all flake8 checks."""
    parser = argparse.ArgumentParser(
        description='Run all flake8 checks (compilation, tests, benchmarks)',
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
        '--only',
        choices=['compilation', 'tests', 'benchmarks'],
        help='Run only specific type of checks'
    )
    
    parser.add_argument(
        '--skip',
        choices=['compilation', 'tests', 'benchmarks'],
        action='append',
        default=[],
        help='Skip specific type of checks (can be used multiple times)'
    )
    
    parser.add_argument(
        '--fail-fast',
        action='store_true',
        help='Stop on first failure'
    )
    
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Run checks in parallel (experimental)'
    )
    
    args = parser.parse_args()
    
    # Determine which checks to run
    all_checks = ['compilation', 'tests', 'benchmarks']
    
    if args.only:
        checks_to_run = [args.only]
    else:
        checks_to_run = [check for check in all_checks if check not in args.skip]
    
    print("🚀 Starting comprehensive flake8 checks")
    print(f"Checks to run: {', '.join(checks_to_run)}")
    print(f"Target paths: {', '.join(args.paths)}")
    
    # Script mapping
    script_map = {
        'compilation': 'flake8_compilation.py',
        'tests': 'flake8_tests.py',
        'benchmarks': 'flake8_benchmarks.py'
    }
    
    # Results storage
    results = {}
    overall_start_time = time.time()
    
    # Run each check
    for check_name in checks_to_run:
        script_name = script_map[check_name]
        
        print_section_header(f"{check_name.upper()} CHECKS", "🎯")
        
        # Prepare arguments
        check_args = args.paths.copy()
        if args.verbose:
            check_args.append('--verbose')
        
        # Add check-specific arguments
        if check_name == 'tests':
            if args.verbose:
                check_args.extend(['--analyze', '--run-tests'])
        elif check_name == 'benchmarks':
            if args.verbose:
                check_args.extend(['--analyze', '--run-benchmarks'])
        
        # Run the check
        start_time = time.time()
        returncode, stdout, stderr = run_script(script_name, check_args, args.verbose)
        end_time = time.time()
        duration = end_time - start_time
        
        # Store results
        results[check_name] = {
            'returncode': returncode,
            'stdout': stdout,
            'stderr': stderr,
            'duration': duration
        }
        
        # Print immediate results
        if returncode == 0:
            print(f"✅ {check_name.upper()} checks PASSED ({format_duration(duration)})")
        else:
            print(f"❌ {check_name.upper()} checks FAILED ({format_duration(duration)})")
        
        # Print output if not verbose (verbose already shows it)
        if not args.verbose and stdout:
            print("Output:")
            for line in stdout.split('\n')[-10:]:  # Show last 10 lines
                if line.strip():
                    print(f"  {line}")
        
        if stderr:
            print("Errors:")
            for line in stderr.split('\n'):
                if line.strip():
                    print(f"  {line}")
        
        # Fail fast if requested
        if args.fail_fast and returncode != 0:
            print(f"\n💥 Stopping due to --fail-fast after {check_name} failure")
            break
    
    overall_end_time = time.time()
    overall_duration = overall_end_time - overall_start_time
    
    # Print comprehensive summary
    print_results_summary(results)
    
    print(f"\n⏱️  Total execution time: {format_duration(overall_duration)}")
    
    # Determine exit code
    failed_checks = [name for name, result in results.items() if result['returncode'] != 0]
    
    if not failed_checks:
        print("\n🎉 All flake8 checks passed successfully!")
        return 0
    else:
        print(f"\n💔 {len(failed_checks)} check(s) failed: {', '.join(failed_checks)}")
        
        print("\n💡 Next steps:")
        print("  1. Review the detailed error messages above")
        print("  2. Run individual scripts with --verbose for more details:")
        for failed_check in failed_checks:
            script_name = script_map[failed_check]
            print(f"     python scripts/{script_name} --verbose")
        print("  3. Fix the issues and re-run this script")
        
        return 1


if __name__ == '__main__':
    sys.exit(main())
