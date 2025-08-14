# Flake8 Scripts Documentation

This document provides comprehensive documentation for the flake8 linting scripts created for this project. These scripts provide specialized linting for compilation, unit tests, and benchmark testing.

## Overview

The project includes four main flake8 scripts:

1. **`flake8_compilation.py`** - Validates syntax and compilation errors
2. **`flake8_tests.py`** - Validates unit test code quality  
3. **`flake8_benchmarks.py`** - Validates benchmark and performance code
4. **`run_all_flake8.py`** - Orchestrates all three types of checks

## Quick Start

```bash
# Install dependencies
pip install -e ".[lint]"

# Run all checks
python scripts/run_all_flake8.py

# Run with verbose output
python scripts/run_all_flake8.py --verbose

# Run only specific checks
python scripts/run_all_flake8.py --only compilation
python scripts/run_all_flake8.py --skip tests
```

## Configuration

### `.flake8` Configuration File

The project includes a comprehensive `.flake8` configuration file that:

- Sets maximum line length to 88 characters (matching Black formatter)
- Sets maximum complexity to 17
- Includes per-file ignores for tests and special directories
- Excludes common build and cache directories
- Configures docstring conventions (Google style)

### pyproject.toml Integration

Flake8 and related plugins are included in the `[project.optional-dependencies.lint]` section:

```toml
lint = [
  "flake8>=7.0.0",
  "flake8-bugbear>=24.0.0",
  "flake8-docstrings>=1.7.0",
  "flake8-import-order>=0.18.2",
  "flake8-comprehensions>=3.14.0",
  "flake8-simplify>=0.21.0",
]
```

## Individual Scripts

### 1. Compilation Checks (`flake8_compilation.py`)

**Purpose**: Validates Python syntax and catches compilation errors that would prevent code execution.

**Usage**:
```bash
python scripts/flake8_compilation.py [--verbose] [--fix] [paths...]
```

**Features**:
- Basic Python compilation checking
- Flake8 with compilation-focused error codes
- Catches syntax errors, undefined names, import issues
- Supports multiple paths and recursive directory scanning

**Focus Areas**:
- Runtime errors (E9 series)
- Undefined names (F821, F822)
- Import issues (F401, F811)
- Syntax warnings (W6 series)

**Example**:
```bash
# Check entire project
python scripts/flake8_compilation.py

# Check specific directory with verbose output
python scripts/flake8_compilation.py --verbose data_structures/

# Check multiple paths
python scripts/flake8_compilation.py sorts/ algorithms/
```

### 2. Unit Test Checks (`flake8_tests.py`)

**Purpose**: Validates unit test code quality and ensures proper testing practices.

**Usage**:
```bash
python scripts/flake8_tests.py [--run-tests] [--analyze] [--verbose] [paths...]
```

**Features**:
- Automatically finds test files (test_*.py, *_test.py, tests.py, tests/ directories)
- Test-specific linting rules (relaxed docstring requirements)
- Optional pytest collection validation
- Test structure analysis

**Test File Detection**:
- Files starting with `test_`
- Files ending with `_test.py`
- Files named `tests.py`
- Any Python files in `tests/` directories

**Example**:
```bash
# Find and check all test files
python scripts/flake8_tests.py

# Check tests and run pytest collection
python scripts/flake8_tests.py --run-tests

# Analyze test structure
python scripts/flake8_tests.py --analyze --verbose
```

### 3. Benchmark Checks (`flake8_benchmarks.py`)

**Purpose**: Validates benchmark and performance testing code quality.

**Usage**:
```bash
python scripts/flake8_benchmarks.py [--run-benchmarks] [--analyze] [--create-sample DIR] [paths...]
```

**Features**:
- Intelligent benchmark file detection (name and content-based)
- Performance-code specific linting rules
- Benchmark structure analysis
- Sample benchmark file generation

**Benchmark File Detection**:
- Files with 'benchmark', 'perf', 'speed', 'timing' in name
- Files in 'benchmarks/' or 'performance/' directories
- Content analysis for timing-related code patterns

**Example**:
```bash
# Find and check all benchmark files
python scripts/flake8_benchmarks.py

# Analyze benchmark patterns
python scripts/flake8_benchmarks.py --analyze

# Create a sample benchmark file
python scripts/flake8_benchmarks.py --create-sample benchmarks/

# Run benchmark validation
python scripts/flake8_benchmarks.py --run-benchmarks --verbose
```

### 4. Orchestration Script (`run_all_flake8.py`)

**Purpose**: Runs all three types of flake8 checks in a coordinated manner.

**Usage**:
```bash
python scripts/run_all_flake8.py [--only TYPE] [--skip TYPE] [--fail-fast] [--verbose] [paths...]
```

**Features**:
- Runs all checks with timing information
- Comprehensive summary reporting
- Selective execution (--only, --skip)
- Fail-fast option for CI/CD pipelines
- Detailed error reporting

**Example**:
```bash
# Run all checks
python scripts/run_all_flake8.py

# Run only compilation checks
python scripts/run_all_flake8.py --only compilation

# Skip test checks
python scripts/run_all_flake8.py --skip tests

# Fail fast on first error
python scripts/run_all_flake8.py --fail-fast

# Verbose output with analysis
python scripts/run_all_flake8.py --verbose
```

## Integration with Development Workflow

### Pre-commit Hooks

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: flake8-compilation
      name: Flake8 Compilation Checks
      entry: python scripts/flake8_compilation.py
      language: system
      pass_filenames: false
    
    - id: flake8-tests
      name: Flake8 Test Checks
      entry: python scripts/flake8_tests.py
      language: system
      pass_filenames: false
```

### GitHub Actions / CI Integration

```yaml
- name: Run Flake8 Checks
  run: |
    pip install -e ".[lint]"
    python scripts/run_all_flake8.py --fail-fast
```

### Makefile Integration

```makefile
lint-compilation:
	python scripts/flake8_compilation.py

lint-tests:
	python scripts/flake8_tests.py --run-tests

lint-benchmarks:
	python scripts/flake8_benchmarks.py --run-benchmarks

lint-all:
	python scripts/run_all_flake8.py

lint-verbose:
	python scripts/run_all_flake8.py --verbose
```

## Error Code Reference

### Compilation-Focused Codes
- **E9**: Runtime errors, syntax errors
- **F63**: Invalid syntax in docstrings
- **F7**: Late binding issues
- **F82**: Undefined name in __all__
- **F401**: Imported but unused
- **F821**: Undefined name
- **W6**: Syntax warnings

### Test-Specific Considerations
- Relaxed docstring requirements (D100-D104)
- Allows assert statements (S101)
- Slightly higher complexity tolerance
- Longer line length allowed for test setup

### Benchmark-Specific Adjustments
- Higher complexity tolerance for benchmark scenarios
- Relaxed import positioning (E402)
- Allows timing loop patterns (B007)
- Focus on performance measurement code quality

## Troubleshooting

### Common Issues

1. **"flake8 not found"**
   ```bash
   pip install -e ".[lint]"
   ```

2. **No files found**
   - Check file naming conventions
   - Use `--verbose` to see search patterns
   - Verify paths are correct

3. **Too many errors**
   - Start with compilation checks first
   - Use individual scripts to focus on specific issues
   - Consider using `--exclude` for problematic directories

4. **Performance issues**
   - Run on specific directories instead of entire project
   - Use `--skip` to avoid unnecessary checks
   - Consider running checks in parallel (experimental)

### Debugging Tips

```bash
# Debug file detection
python scripts/flake8_tests.py --verbose --analyze

# Check specific file types
python scripts/flake8_compilation.py --verbose specific_file.py

# Get detailed error information
python scripts/run_all_flake8.py --verbose --fail-fast
```

## Customization

### Adding New Error Codes

Edit the `select_codes` list in each script:

```python
select_codes = [
    'E',     # pycodestyle errors
    'W',     # pycodestyle warnings
    'F',     # pyflakes
    'B',     # flake8-bugbear
    'NEW',   # Your new plugin
]
```

### Modifying Ignore Patterns

Update the `ignore_codes` list or modify `.flake8` configuration:

```python
ignore_codes = [
    'E203',  # whitespace before ':'
    'NEW123', # Your custom ignore
]
```

### Custom File Detection

Modify the detection functions:

```python
def is_benchmark_file(file_path: Path) -> bool:
    # Add your custom detection logic
    return 'my_pattern' in file_path.name
```

## Best Practices

1. **Run regularly**: Integrate into development workflow
2. **Start with compilation**: Fix syntax errors before style issues
3. **Use verbose mode**: For debugging and understanding issues
4. **Customize for project**: Adjust configurations based on project needs
5. **Document exceptions**: Use inline comments for necessary ignores
6. **Review periodically**: Update configurations as project evolves

## Contributing

When modifying these scripts:

1. Test on the actual project codebase
2. Update documentation for new features
3. Maintain backward compatibility
4. Add appropriate error handling
5. Follow the existing code style

## Support

For issues or questions:

1. Check this documentation first
2. Run with `--verbose` for detailed output
3. Test individual scripts to isolate issues
4. Review the `.flake8` configuration
5. Check flake8 plugin documentation for specific error codes
