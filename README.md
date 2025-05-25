# 🔍 Compat - Python Package Conflict Detection Tool

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/EaminC/compat)
[![Python](https://img.shields.io/badge/python-3.7+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Intelligent Python package conflict detection tool with PyPI-based dependency analysis, multiple detection modes, and smart suggestions.

## ✨ Key Features

- 🎯 **Accurate Conflict Detection** - PyPI-based dependency analysis
- 🔧 **Multiple Detection Modes** - From simple YES/NO to comprehensive reports
- 📋 **Requirements.txt Analysis** - Intelligent comparison of multiple dependency files
- 🧠 **Smart Suggestions** - Typo corrections, similar package recommendations, version suggestions
- ⚙️ **System-Level Analysis** - CUDA/cuDNN version conflict detection

## 🚀 Quick Start

```bash
# Clone the project
git clone https://github.com/EaminC/compat.git
cd compat

# Simple compatibility check
python compat-cli.py simple "requests" "urllib3"
# Output: YES

# Detailed analysis (default mode)
python compat-cli.py "tensorflow==2.16.0" "torch==2.2.0"

# Enhanced mode (recommended)
python compat-cli.py enhanced "pandas>=1.3.0" "numpy<1.21.0" --verbose

# Requirements.txt analysis
python compat-cli.py requirements file1.txt file2.txt --output report.txt
```

## 📋 Detection Modes

### 1. Simple Mode - Automation Friendly

```bash
python compat-cli.py simple "package1==1.0.0" "package2>=2.0.0"
```

Returns only YES (compatible) or NO (incompatible), perfect for scripts and CI/CD pipelines.

### 2. Check Mode - Default Mode

```bash
python compat-cli.py "requests==2.25.0" "urllib3==2.0.0"
```

Comprehensive PyPI-based analysis with intelligent suggestions and version recommendations.

### 3. Enhanced Mode - Recommended

```bash
python compat-cli.py enhanced "tensorflow==2.16.0" "torch==2.2.0" --verbose
```

Integrates pip dependency resolver with system-level conflict detection and multi-layer analysis.

### 4. Requirements Mode - File Comparison

```bash
python compat-cli.py requirements web_requirements.txt ml_requirements.txt
```

Intelligent analysis of compatibility between multiple requirements.txt files.

## 🎯 Example Output

### Conflict Detection

```
❌ Conflict Type: Dependency Conflict
Severity: high
Result: Dependency version conflicts detected:
requests v2.25.0 requires urllib3 <1.27,>=1.21.1, but you specified urllib3==2.0.0

🎯 Suggested versions:
   • 1.26.18
   • 1.26.17
   • 1.26.16
```

### Smart Suggestions

```
🔍 Conflict Type: Package Not Found
Result: Package 'reqests' not found on PyPI

💡 Suggestions:
   🔤 Possible typo corrections:
      • requests
   📦 Similar package names:
      • requests (similarity: 0.783)
```

## 📊 Command Reference

| Command        | Description                       | Best For                 |
| -------------- | --------------------------------- | ------------------------ |
| `simple`       | Returns only YES/NO               | Automation, scripts      |
| `check`        | Default hypothetical analysis     | General use, development |
| `enhanced`     | Pip-integrated advanced detection | Production environments  |
| `requirements` | Requirements.txt comparison       | Project planning, audits |

### Global Options

- `--version` - Show version information
- `--verbose, -v` - Enable detailed output
- `--no-suggestions` - Disable intelligent suggestions
- `--output, -o FILE` - Save report to file

## 🔧 Technical Features

- **Intelligent Caching** - Reduces PyPI API calls
- **Version Constraint Parsing** - Supports all pip version operators (~=, >=, <=, !=, ==, >, <)
- **Error Recovery** - Graceful handling of network issues
- **Modular Design** - Clean code architecture

## 📁 Example Files

The `data/examples/` directory contains sample requirements.txt files for testing:

- `web_app_requirements.txt` - Web application dependencies
- `data_science_requirements.txt` - Machine learning packages
- `conflicting_requirements.txt` - Deliberately conflicting dependencies

## 🆕 v2.0.0 Major Improvements

- ✅ **Critical Bug Fixes** - Fixed `requests==2.25.0` vs `urllib3==2.0.0` conflict detection issue
- 🆕 **Requirements.txt Analysis** - Complete dependency file compatibility analysis
- 🚀 **Pip Integration** - Direct integration with pip's dependency resolver
- 🧠 **Smart Suggestions** - Enhanced typo correction and version recommendations

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ for the Python community**

_For support, feature requests, or bug reports, please open an issue on GitHub._
