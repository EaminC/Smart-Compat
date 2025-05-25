# 📦 Package Conflict Detection Tool

A comprehensive Python package conflict detection tool with intelligent features and multiple detection modes.

## 🌟 Features

- **✅ Version Compatibility Detection** - Check if specified versions are compatible
- **✅ Package Existence Validation** - Verify if versions exist on PyPI
- **✅ Smart Suggestions** - Spelling correction and similar package suggestions
- **✅ System-Level Conflict Detection** - Detect CUDA, cuDNN version conflicts
- **✅ Transitive Dependency Analysis** - Check indirect dependency version conflicts
- **✅ Hypothetical Detection** - PyPI-based analysis independent of local installations

## 🚀 Quick Start

### Installation

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/EaminC/Smart-Compat.git
cd compat
```

### Basic Usage (Recommended)

```bash
# Check compatibility between two packages (hypothetical detection)
python compat-cli.py "tensorflow==2.8.0" "urllib3"
python compat-cli.py "pandas" "numpy"

# Equivalent to
python compat-cli.py check "tensorflow==2.8.0" "urllib3"
```

### Verbose Output

```bash
python compat-cli.py "tensorflow==2.8.0" "torch==1.12.0" --verbose
```

## 🔧 Detection Modes

### 1. Requirements.txt Analysis (New!)

Analyzes compatibility between multiple requirements.txt files with intelligent version constraint resolution.

```bash
python compat-cli.py requirements data/examples/web_app_requirements.txt data/examples/conflicting_requirements.txt
```

**Features:**

- **Smart Version Constraint Analysis**: Correctly identifies compatible vs incompatible version specifications
- **Cross-dependency Conflict Detection**: Finds conflicts between dependencies of different packages
- **Detailed Reporting**: Line-by-line analysis with conflict explanations
- **Report Export**: Save detailed analysis reports to file

**Example Output:**

```
============================================================
📋 Requirements.txt Compatibility Analysis Report
============================================================
File 1: web_app_requirements.txt
File 2: conflicting_requirements.txt

📊 Summary:
   • Total unique packages: 11
   • Compatible packages: 0
   • Version conflicts: 4
   • Dependency conflicts: 2

❌ Overall Status: INCOMPATIBLE
   Found 4 critical conflicts

⚠️ Version Conflicts:
   • flask:
     - web_app_requirements.txt: >=2.0.0,<3.0.0 (line 4)
     - conflicting_requirements.txt: ==1.1.4 (line 4)
     - Conflict type: Version Constraint Incompatibility
```

### 2. Enhanced Detection (Recommended)

Integrates pip's dependency resolver with advanced version constraint analysis for the most accurate conflict detection.

```bash
python compat-cli.py enhanced "tensorflow==2.16.1" "torch==2.2.0" --verbose
```

**Features:**

- **Pip Integration**: Uses pip's actual dependency resolution engine
- **Advanced Version Constraints**: Supports all pip version operators (~=, >=, <=, !=, ==, >, <)
- **Multi-layer Analysis**: Combines PyPI data, system dependencies, and pip simulation
- **Intelligent Explanations**: Human-readable version constraint explanations

**Example Output:**

```
🚀 Enhanced Mode: Pip-integrated enhanced conflict detection
❌ Conflict Type: Dependency Conflict
Severity: high
Result: System-level conflicts detected:
• tensorflow requires CUDA 12.3, but torch requires CUDA 11.8

🔧 Detection Methods Used:
   • PyPI-based hypothetical analysis
   • System-level dependency analysis
   • Pip dependency resolver simulation
   • Advanced version constraint analysis

📋 Version Constraints:
   Package 1: Exactly version 2.16.1
   Package 2: Exactly version 2.2.0
```

### 3. Hypothetical Detection (Default)

Completely PyPI-based analysis, independent of local installation status.

```bash
python compat-cli.py check "package1" "package2"
python compat-cli.py "package1" "package2"  # Simplified syntax
```

**Example Output:**

```
✅ Conflict Type: No Conflict
Severity: low
Result: No conflicts found: tensorflow v2.8.0 and urllib3 v2.4.0 are compatible
```

### 4. Advanced Detection

Includes system-level dependencies (CUDA, etc.) and transitive dependency conflict detection.

```bash
python compat-cli.py advanced "tensorflow" "torch"
```

**Example Output:**

```
❌ Conflict Type: Dependency Conflict
Severity: high
Result: System-level conflicts detected:
• tensorflow requires CUDA 11.2, but torch requires CUDA 11.3

🔍 Advanced Conflict Analysis:
   1. 🖥️ System Dependency: tensorflow requires CUDA 11.2, but torch requires CUDA 11.3
      • tensorflow: CUDA 11.2
      • torch: CUDA 11.3
```

### 5. Basic Detection

Basic version and dependency conflict detection.

```bash
python compat-cli.py basic "requests==2.28.0" "urllib3"
```

## 🧪 Testing

Run the complete test suite:

```bash
python compat-cli.py test --verbose
```

**Test Coverage:**

- ✅ Basic conflict detection
- ✅ Advanced conflict detection (CUDA, transitive dependencies)
- ✅ Hypothetical compatibility detection
- ✅ Version existence validation
- ✅ Package name suggestion functionality

## 📋 Command Line Options

### Global Options

- `--version` - Show version information
- `--verbose, -v` - Enable verbose output
- `--no-suggestions` - Disable package name suggestions

### Commands

| Command        | Description                                                           |
| -------------- | --------------------------------------------------------------------- |
| `requirements` | Requirements.txt compatibility analysis (recommended for files)       |
| `enhanced`     | Pip-integrated enhanced conflict detection (recommended for packages) |
| `check`        | Hypothetical compatibility detection (default)                        |
| `advanced`     | Advanced conflict detection with system-level analysis                |
| `basic`        | Basic conflict detection                                              |
| `test`         | Run test suite                                                        |

## 🎯 Use Cases

- **📋 Dependency Planning** - Evaluate package combination compatibility before installation
- **🔍 Version Selection** - Find compatible version combinations
- **⚠️ Risk Assessment** - Discover potential system-level conflicts
- **📊 Ecosystem Analysis** - Research Python package ecosystem interactions

## 📄 Output Examples

### Dependency Version Constraint Conflicts

```
❌ Conflict Type: Dependency Conflict
Severity: high
Result: Dependency version conflicts detected:
requests v2.25.0 requires urllib3 <1.27,>=1.21.1, but you specified urllib3==2.0.0

📦 Package Information:
   • requests v2.25.0
     └─ Python HTTP for Humans.
   • urllib3 v2.0.0
     └─ HTTP library with thread-safe connection pooling, file post, and more.
```

### No Conflicts

```
✅ Conflict Type: No Conflict
Severity: low
Result: No conflicts found: tensorflow v2.8.0 and urllib3 v2.4.0 are compatible

📦 Package Information:
   • tensorflow v2.8.0
     └─ TensorFlow is an open source machine learning framework
   • urllib3 v2.4.0
     └─ HTTP library with thread-safe connection pooling
```

### CUDA Version Conflicts

```
❌ Conflict Type: Dependency Conflict
Severity: high
Result: System-level conflicts detected:
• tensorflow requires CUDA 11.2, but torch requires CUDA 11.3

🔍 Advanced Conflict Analysis:
   1. 🖥️ System Dependency: tensorflow requires CUDA 11.2, but torch requires CUDA 11.3
      • tensorflow==2.8.0: CUDA 11.2
      • torch==1.12.0: CUDA 11.3
```

### Version Not Found

```
❌ Conflict Type: Version Conflict
Severity: high
Result: Version not found: requests v2.1.099 does not exist on PyPI

📋 Available versions:
   • 2.1.0
   • 2.19.0
   • 2.10.0
   • 2.11.0
   • 2.12.0

🆕 Latest version: 2.9.2
```

### Package Name Suggestions

```
🔍 Conflict Type: Package Not Found
Severity: info
Result: Package 'reqests' not found on PyPI

💡 Suggestions:
   🔤 Possible typo corrections:
      • requests
   📦 Similar package names:
      • requests (similarity: 0.78)
```

## 🏗️ Architecture

The tool consists of four main detector classes:

1. **PackageConflictDetector** - Basic version and dependency conflict detection
2. **AdvancedConflictDetector** - Adds CUDA version conflicts and transitive dependency analysis
3. **HypotheticalConflictDetector** - Complete PyPI-based analysis independent of local installations
4. **EnhancedConflictDetector** - Integrates pip's dependency resolver with advanced version constraint analysis

### Key Design Principles

- **Strict Version Handling**: When a specified version doesn't exist, the tool reports an error instead of falling back to other versions
- **PyPI-First Approach**: Hypothetical mode queries PyPI directly for accurate version information
- **Intelligent Suggestions**: Provides spelling corrections and similar package recommendations
- **Comprehensive Conflict Detection**: Covers system-level dependencies, transitive conflicts, and basic version mismatches

## 📁 Project Structure

```
compat/
├── compat-cli.py              # Unified CLI entry point
├── compat/
│   ├── core/
│   │   ├── detector.py        # Basic conflict detector
│   │   ├── advanced_detector.py  # Advanced conflict detector
│   │   ├── hypothetical_detector.py  # Hypothetical detector
│   │   ├── enhanced_detector.py     # Enhanced detector with pip integration
│   │   ├── requirements_analyzer.py # Requirements.txt compatibility analyzer
│   │   ├── pip_resolver.py    # Pip dependency resolver integration
│   │   ├── version_resolver.py      # Advanced version constraint resolver
│   │   └── types.py           # Common types and enums
│   └── utils/
│       └── suggestions.py     # Package name suggestions
├── data/
│   ├── examples/              # Example requirements.txt files
│   │   ├── web_app_requirements.txt
│   │   ├── data_science_requirements.txt
│   │   ├── conflicting_requirements.txt
│   │   └── test_requirements*.txt
│   └── reports/               # Generated analysis reports
└── README.md                  # This file
```

## 🔄 Recent Improvements

### Critical Bug Fixes

- **Fixed Dependency Version Constraint Detection**: Resolved critical issue where the tool failed to detect real dependency conflicts like `requests==2.25.0` vs `urllib3==2.0.0`
- **Improved Dependency Parsing**: Enhanced regex parsing to correctly handle complex dependency specifications with parentheses and multiple constraints (e.g., `urllib3 (<1.27,>=1.21.1)`)
- **Accurate Version Constraint Validation**: Implemented proper version constraint checking using the `packaging` library with fallback to custom logic
- **Fixed Fallback Logic**: Removed problematic fallback from PyPI to local installations when specified versions don't exist
- **Strict Version Validation**: Tool now correctly reports when requested versions don't exist on PyPI
- **Improved Error Messaging**: Clear distinction between package not found and version not found scenarios
- **Version Suggestion Enhancement**: Fixed latest version detection and provided intelligent similar version suggestions

### Enhanced Features

- **Pip Integration**: Added pip dependency resolver integration for more accurate conflict detection
- **Advanced Version Constraints**: Complete support for all pip version operators (~=, >=, <=, !=, ==, >, <)
- **Multi-layer Analysis**: Combines PyPI data, system dependencies, pip simulation, and version constraint analysis
- **Better Output Formatting**: Eliminated duplicate version suggestions and enhanced readability
- **Comprehensive Testing**: Full test suite covering all detection modes and edge cases
- **Unified CLI**: Single entry point with multiple subcommands for different detection modes

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🔗 Related Tools

- [pip-tools](https://github.com/jazzband/pip-tools) - A set of tools to keep your pinned Python dependencies fresh
- [pipdeptree](https://github.com/tox-dev/pipdeptree) - Display dependency tree of packages
- [safety](https://github.com/pyupio/safety) - Check Python dependencies for known security vulnerabilities
