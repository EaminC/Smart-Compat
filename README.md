# 🔍 Compat - Advanced Python Package Conflict Detection Tool

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/EaminC/compat)
[![Python](https://img.shields.io/badge/python-3.7+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A comprehensive and intelligent Python package conflict detection tool with advanced PyPI-based analysis, smart suggestions, and multiple detection modes.

## 🌟 Key Features

- **🎯 Accurate Conflict Detection** - PyPI-based analysis with proper dependency parsing
- **🔧 Multiple Detection Modes** - From simple YES/NO to comprehensive reports
- **📋 Requirements.txt Analysis** - Compare multiple dependency files intelligently
- **🧠 Smart Suggestions** - Typo corrections, similar packages, and version recommendations
- **⚙️ System-Level Analysis** - CUDA/cuDNN version conflicts and transitive dependencies
- **🚀 Pip Integration** - Leverages pip's dependency resolver for maximum accuracy
- **📊 Professional Reports** - Detailed analysis with export capabilities

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/EaminC/compat.git
cd compat
```

### Basic Usage

```bash
# Simple compatibility check
python compat-cli.py simple "requests" "urllib3"
# Output: YES

# Detailed analysis (default mode)
python compat-cli.py "tensorflow==2.16.0" "torch==2.2.0"

# Enhanced mode with pip integration
python compat-cli.py enhanced "pandas>=1.3.0" "numpy<1.21.0" --verbose

# Requirements.txt analysis
python compat-cli.py requirements file1.txt file2.txt --output report.txt
```

## 📋 Detection Modes

### 1. 🎯 Simple Mode (Automation-Friendly)

Perfect for scripts and CI/CD pipelines - returns only YES (compatible) or NO (incompatible).

```bash
python compat-cli.py simple "package1==1.0.0" "package2>=2.0.0"
```

**Use Cases:**

- Automated dependency validation
- CI/CD pipeline integration
- Quick compatibility checks

### 2. 🔍 Check Mode (Default)

Comprehensive PyPI-based hypothetical analysis with intelligent suggestions.

```bash
python compat-cli.py check "requests==2.25.0" "urllib3==2.0.0"
# or simply:
python compat-cli.py "requests==2.25.0" "urllib3==2.0.0"
```

**Features:**

- Version existence validation on PyPI
- Dependency constraint checking
- Smart package name suggestions
- Version recommendation system

**Example Output:**

```
❌ Conflict Type: Dependency Conflict
Severity: high
Result: Dependency version conflicts detected:
requests v2.25.0 requires urllib3 <1.27,>=1.21.1, but you specified urllib3==2.0.0

🎯 Similar versions:
   • 1.26.18
   • 1.26.17
   • 1.26.16
```

### 3. 🚀 Enhanced Mode (Recommended)

Advanced analysis with pip dependency resolver integration and multi-layer conflict detection.

```bash
python compat-cli.py enhanced "tensorflow==2.16.0" "torch==2.2.0" --verbose
```

**Advanced Features:**

- **Pip Integration**: Uses pip's actual dependency resolution engine
- **System Dependencies**: CUDA/cuDNN version conflict detection
- **Version Constraints**: Complete support for all pip operators (~=, >=, <=, !=, ==, >, <)
- **Multi-layer Analysis**: Combines PyPI data, pip simulation, and constraint analysis

**Example Output:**

```
🚀 Enhanced Mode: Pip-integrated enhanced conflict detection
❌ Conflict Type: Dependency Conflict
Result: System-level conflicts detected:
• tensorflow requires CUDA 12.3, but torch requires CUDA 11.8

🔧 Detection Methods Used:
   • PyPI-based hypothetical analysis
   • System-level dependency analysis
   • Pip dependency resolver simulation
   • Advanced version constraint analysis

✅ Confirmed by pip dependency resolver
```

### 4. 📊 Requirements.txt Analysis

Intelligent compatibility analysis between multiple requirements.txt files with detailed reporting.

```bash
python compat-cli.py requirements web_requirements.txt ml_requirements.txt
```

**Capabilities:**

- **Smart Constraint Analysis**: Identifies compatible vs incompatible version specifications
- **Cross-dependency Detection**: Finds conflicts between dependencies of different packages
- **Line-by-line Analysis**: Precise conflict location reporting
- **Professional Reports**: Export detailed analysis to file

**Example Output:**

```
============================================================
📋 Requirements.txt Compatibility Analysis Report
============================================================
File 1: web_requirements.txt
File 2: ml_requirements.txt

📊 Summary:
   • Total unique packages: 15
   • Compatible packages: 8
   • Version conflicts: 3
   • Dependency conflicts: 1

❌ Overall Status: INCOMPATIBLE
   Found 3 critical conflicts

⚠️ Version Conflicts:
   • numpy:
     - web_requirements.txt: >=1.19.0 (line 3)
     - ml_requirements.txt: <1.19.0 (line 5)
     - Conflict type: Version Constraint Incompatibility
```

## 🎯 Advanced Features

### Smart Suggestions System

**Package Name Corrections:**

```bash
python compat-cli.py check "reqests" "numpy"
```

```
🔍 Conflict Type: Package Not Found
Result: Package 'reqests' not found on PyPI

💡 Suggestions:
   🔤 Possible typo corrections:
      • requests
   📦 Similar package names:
      • requests (similarity: 0.783)
```

**Version Recommendations:**

```bash
python compat-cli.py check "numpy==999.0.0" "pandas"
```

```
❌ Conflict Type: Version Conflict
Result: Version not found: numpy v999.0.0 does not exist on PyPI

🎯 Similar versions:
   • 1.26.2
   • 1.26.1
   • 1.26.0

🆕 Latest version: 1.26.2
```

### System-Level Conflict Detection

Detects conflicts in system dependencies like CUDA versions:

```bash
python compat-cli.py enhanced "tensorflow==2.8.0" "torch==1.12.0"
```

```
❌ System-level conflicts detected:
• tensorflow requires CUDA 11.2, but torch requires CUDA 11.3
• tensorflow requires cuDNN 8.1, but torch requires cuDNN 8.3
```

## 📋 Command Reference

### Global Options

| Option             | Description                     |
| ------------------ | ------------------------------- |
| `--version`        | Show version information        |
| `--verbose, -v`    | Enable detailed output          |
| `--no-suggestions` | Disable intelligent suggestions |

### Commands

| Command        | Description                       | Best For                 |
| -------------- | --------------------------------- | ------------------------ |
| `simple`       | YES/NO output only                | Automation, scripting    |
| `check`        | Default hypothetical analysis     | General use, development |
| `enhanced`     | Pip-integrated advanced detection | Production environments  |
| `requirements` | Requirements.txt comparison       | Project planning, audits |

### Requirements Command Options

| Option              | Description                         |
| ------------------- | ----------------------------------- |
| `--output, -o FILE` | Save detailed report to file        |
| `--verbose, -v`     | Include additional analysis details |

## 🏗️ Architecture

### Modular Design

```
compat/
├── detectors/           # Core conflict detection engines
│   ├── basic.py        # Base functionality
│   ├── advanced.py     # System-level analysis
│   ├── hypothetical.py # PyPI-based detection
│   └── enhanced.py     # Pip integration
├── analyzers/          # Specialized analysis tools
│   └── requirements_analyzer.py
├── utils/              # Supporting utilities
│   ├── suggestions.py  # Smart recommendations
│   ├── pip_resolver.py # Pip integration
│   └── version_resolver.py # Version constraints
└── core/
    └── types.py       # Common data structures
```

### Detection Engine Hierarchy

1. **PackageConflictDetector** (Basic)

   - Core version and dependency validation
   - PyPI package existence checking
   - Basic conflict resolution

2. **AdvancedConflictDetector** (Advanced)

   - Extends basic with system-level analysis
   - CUDA/cuDNN version conflict detection
   - Transitive dependency analysis

3. **HypotheticalConflictDetector** (Default)

   - Complete PyPI-based analysis
   - Independent of local installations
   - Enhanced error handling and suggestions

4. **EnhancedConflictDetector** (Recommended)
   - Integrates pip's dependency resolver
   - Multi-layer conflict detection
   - Advanced version constraint analysis

## 🔧 Technical Highlights

### Dependency Parsing Engine

Handles complex dependency specifications with robust regex parsing:

```python
# Correctly parses complex constraints like:
"urllib3 (<1.27,>=1.21.1)"
"tensorflow-gpu>=2.0.0,<3.0.0"
"numpy~=1.19.0"
```

### Version Constraint Validation

Uses the `packaging` library with intelligent fallback for maximum compatibility:

```python
# Supports all pip version operators:
">= 1.0.0"    # Greater than or equal
"~= 1.4.2"    # Compatible release
"!= 1.5"      # Not equal
"< 2.0, >= 1.5"  # Multiple constraints
```

### PyPI Integration

Direct PyPI API integration for real-time package information:

- Version existence validation
- Latest version detection
- Available version enumeration
- Dependency specification parsing

## 📊 Use Cases

### Development Workflows

- **Pre-installation Validation**: Check compatibility before installing packages
- **Version Planning**: Find compatible version combinations
- **Dependency Auditing**: Analyze existing dependency files

### Production Environments

- **CI/CD Integration**: Automated compatibility validation in pipelines
- **Risk Assessment**: Identify potential system-level conflicts
- **Environment Migration**: Validate package compatibility across environments

### Research & Analysis

- **Ecosystem Analysis**: Study Python package interaction patterns
- **Conflict Research**: Investigate dependency resolution challenges
- **Version Impact Assessment**: Understand upgrade implications

## 🚀 Performance & Reliability

### Optimized Design

- **Intelligent Caching**: Reduces PyPI API calls with smart caching
- **Timeout Handling**: Graceful handling of network issues
- **Error Recovery**: Robust fallback mechanisms for reliability

### Accuracy Improvements

- **Fixed Critical Bugs**: Resolved dependency parsing failures
- **Enhanced Validation**: Proper version constraint checking
- **Strict Version Handling**: Clear distinction between package and version errors

## 📈 Recent Improvements (v2.0.0)

### Critical Bug Fixes ✅

- **Dependency Detection**: Fixed critical issue where `requests==2.25.0` vs `urllib3==2.0.0` conflicts weren't detected
- **Parsing Engine**: Enhanced regex to handle complex dependency specs like `urllib3 (<1.27,>=1.21.1)`
- **Version Validation**: Implemented proper constraint checking using `packaging` library
- **Error Handling**: Improved distinction between package not found vs version not found

### New Features 🆕

- **Requirements.txt Analysis**: Complete compatibility analysis between dependency files
- **Pip Integration**: Direct integration with pip's dependency resolver
- **Smart Suggestions**: Enhanced typo correction and version recommendations
- **Multi-layer Detection**: Combines PyPI data, system analysis, and pip simulation

### Architecture Improvements 🏗️

- **Modular Design**: Reorganized into logical modules (detectors, analyzers, utils)
- **Unified CLI**: Single entry point with multiple specialized commands
- **Professional Output**: Enhanced formatting and reporting capabilities

## 📁 Example Files

The `data/examples/` directory contains sample requirements.txt files for testing:

- `web_app_requirements.txt` - Typical web application dependencies
- `data_science_requirements.txt` - Machine learning and data science packages
- `conflicting_requirements.txt` - Deliberately conflicting dependencies for testing
- `test_requirements*.txt` - Various test scenarios

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for:

- Code style and standards
- Testing requirements
- Pull request process
- Issue reporting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Tools

- [pip-tools](https://github.com/jazzband/pip-tools) - Dependency management
- [pipdeptree](https://github.com/tox-dev/pipdeptree) - Dependency visualization
- [safety](https://github.com/pyupio/safety) - Security vulnerability scanning
- [pipenv](https://github.com/pypa/pipenv) - Package and virtual environment management

---

**Made with ❤️ for the Python community**

_For support, feature requests, or bug reports, please open an issue on GitHub._
