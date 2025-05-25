# 📁 Example Requirements Files

This directory contains example requirements.txt files to demonstrate the compatibility analysis features of the package conflict detection tool.

## 📋 Available Examples

### 🌐 Web Application Stack

- **File**: `web_app_requirements.txt`
- **Description**: Flask-based web application dependencies
- **Use Case**: Typical web application with database support

### 📊 Data Science Stack

- **File**: `data_science_requirements.txt`
- **Description**: Machine learning and data analysis dependencies
- **Use Case**: Jupyter-based data science projects

### ⚠️ Conflicting Dependencies

- **File**: `conflicting_requirements.txt`
- **Description**: Intentionally conflicting requirements for testing
- **Use Case**: Demonstrates conflict detection capabilities

### 🧪 Test Cases

- **Files**: `test_requirements1.txt`, `test_requirements2.txt`, `test_requirements3.txt`
- **Description**: Simple test cases with various compatibility scenarios

## 🚀 Usage Examples

### Compare Web App vs Data Science

```bash
python compat-cli.py requirements data/examples/web_app_requirements.txt data/examples/data_science_requirements.txt
```

### Test Conflict Detection

```bash
python compat-cli.py requirements data/examples/web_app_requirements.txt data/examples/conflicting_requirements.txt
```

### Generate Detailed Report

```bash
python compat-cli.py requirements data/examples/web_app_requirements.txt data/examples/conflicting_requirements.txt -o data/reports/conflict_analysis.txt
```

### Test Compatible Requirements

```bash
python compat-cli.py requirements data/examples/test_requirements1.txt data/examples/test_requirements3.txt
```

## 📊 Expected Results

- **web_app_requirements.txt vs data_science_requirements.txt**: Should be compatible (different domains)
- **web_app_requirements.txt vs conflicting_requirements.txt**: Should show multiple conflicts
- **test_requirements1.txt vs test_requirements3.txt**: Should be compatible with smart version resolution
- **test_requirements1.txt vs test_requirements2.txt**: Should show version and dependency conflicts
