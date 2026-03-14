# Project Structure Guide

## Overview

This project has been organized with the following structure for better maintainability:

```
pyhtonTest/
├── src/                          # All Python source code
├── input/                        # Input data (JSON instances)
├── outputs/                      # Auto-generated output directories
└── [documentation files]
```

## Directory Details

### `src/` - Source Code Directory

Contains all Python implementation files:

```
src/
├── pipeline.py                   # Main entry point - orchestrates all 4 tasks
├── config.py                     # Centralized configuration (68 parameters)
├── utils.py                      # Shared utilities
│   ├── setup_logging()           # Configure logging
│   ├── timeout()                 # Context manager for timeouts
│   ├── load_and_validate_instance() # JSON validation
│   └── error handling utilities
│
├── knapsack_solver.py            # Task 1: Classical Exact Solution
│   └── solve_knapsack_batch()
│
├── knapsack_solver_qubo.py       # Task 2: QUBO Formulation
│   └── solve_knapsack_qubo_batch()
│
├── knapsack_qiskit_eigen.py      # Task 3: Quantum Simulation (Qiskit)
│   ├── greedy_knapsack_solver()  # Fallback heuristic
│   └── solve_knapsack_qiskit_batch()
│
├── knapsack_dimod.py             # Task 4: Quantum-Inspired Annealing
│   └── solve_knapsack_dimod_batch()
│
├── analyze_results.py            # Report generation
│   ├── parse_results_file()
│   ├── generate_comparison_report()
│   └── generate_html_report()
│
└── __pycache__/                  # Python bytecode cache (auto-generated)
```

**Key Points:**
- All imports are relative: `from config import ...` (not `from src.config import ...`)
- All files are in the same directory for easy importing
- The `__pycache__/` is auto-generated and can be safely deleted

### `input/` - Input Data Directory

Contains knapsack problem instances in JSON format:

```
input/
├── knapsack_data_6.json          # 6 items
├── knapsack_data_10.json         # 10 items
├── knapsack_data_20.json         # 20 items
├── knapsack_data_50.json         # 50 items
├── knapsack_data_100.json        # 100 items
├── knapsack_data_1000.json       # 1000 items
├── knapsack_data_1000_hard.json  # 1000 items (hard instance)
├── knapsack_data_10000.json      # 10000 items
└── supplier_cover_instance.json  # Alternative format
```

**Format:**
```json
{
  "sets": {
    "P": [1, 2, 3, ..., n]
  },
  "parameters": {
    "b": 50,                    // Knapsack capacity
    "C": {"1": 10, "2": 20, ...},  // Item values
    "a": {"1": 5, "2": 8, ...}    // Item weights
  }
}
```

**Access:** Configured via `INPUT_DIR` in `src/config.py`

### `outputs/` - Output Directory

Auto-generated directory containing timestamped run folders:

```
outputs/
├── run_20260314_220406/          # Run from 2026-03-14 22:04:06
│   ├── risultati_task1.txt       # Task 1 results (exact)
│   ├── risultati_task2_qubo.txt  # Task 2 results (QUBO)
│   ├── risultati_task3_qiskit.txt# Task 3 results (Qiskit)
│   ├── risultati_task4_dimod.txt # Task 4 results (Dimod)
│   ├── benchmark_tempi.csv       # Execution times
│   ├── final_comparison_report.csv # Main comparison report
│   ├── report.html               # Interactive HTML report
│   └── pipeline.log              # Execution log
│
├── run_20260314_222727/          # Another run
│   └── ...
│
└── run_YYYYMMDD_HHMMSS/          # New runs created here
    └── ...
```

**Features:**
- Each run gets a unique timestamp directory
- All outputs are isolated per run
- Easy to compare multiple runs
- Old runs are preserved for reference

**Access:** Configured via `OUTPUT_BASE_DIR` in `src/config.py`

---

## Running the Pipeline

### Correct Way ✅

```bash
# From project root
cd /home/locode/Personale/QML/pyhtonTest

# Run pipeline
uv run src/pipeline.py

# Results appear in
outputs/run_20260314_HHMMSS/
```

### Incorrect Ways ❌

```bash
# DON'T run from src/ directory
cd src
uv run pipeline.py  # ❌ Fails: can't find config.py

# DON'T use absolute src path in import
from src.config import ...  # ❌ Won't work when in src/

# DON'T run individual tasks directly
uv run src/knapsack_solver.py  # ❌ Import errors
```

---

## Import Strategy

### How It Works

**In `src/pipeline.py`:**
```python
from config import INPUT_DIR, CONTINUE_ON_ERROR, OUTPUT_BASE_DIR
from utils import setup_logging, get_memory_usage_mb
from knapsack_solver import solve_knapsack_batch as task1
```

**Why this works:**
1. Python adds the directory of the executing file to `sys.path`
2. When running `uv run src/pipeline.py`, `src/` is added to `sys.path`
3. All imports are relative to `src/`

**In `src/config.py`:**
```python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))    # = src/
PROJECT_ROOT = os.path.dirname(BASE_DIR)                 # = pyhtonTest/
INPUT_DIR = os.path.join(PROJECT_ROOT, "input")          # = pyhtonTest/input/
OUTPUT_BASE_DIR = os.path.join(PROJECT_ROOT, "outputs")  # = pyhtonTest/outputs/
```

**Why this works:**
- Uses `__file__` to find current location dynamically
- Always finds `input/` and `outputs/` in project root
- Works regardless of where the user runs the command

---

## Configuration (src/config.py)

Centralized configuration with 68 parameters:

### File Paths
```python
INPUT_DIR = os.path.join(PROJECT_ROOT, "input")
OUTPUT_BASE_DIR = os.path.join(PROJECT_ROOT, "outputs")
```

### Task Parameters
```python
QISKIT_TIMEOUT_SECONDS = 120          # Qiskit timeout
DIMOD_TIMEOUT_SECONDS = 120           # Dimod timeout
GUROBI_MAX_INSTANCE_SIZE = 100        # Skip if > 100 items
QUBO_PENALTY_MULTIPLIER = 2.0         # Penalty weight
```

### Logging
```python
LOG_LEVEL = "INFO"
LOG_TO_FILE = True
LOG_TO_CONSOLE = True
CONTINUE_ON_ERROR = True
```

**Modify `src/config.py` to tune behavior without touching code!**

---

## Output Files

### Text Results
- `risultati_task1.txt` - Task 1 output (one result per instance)
- `risultati_task2_qubo.txt` - Task 2 output
- `risultati_task3_qiskit.txt` - Task 3 output
- `risultati_task4_dimod.txt` - Task 4 output

Format per file:
```
REPORT RISULTATI - TASK N (...)
==================================================
FILE: knapsack_data_10.json
Solution: 123.45
...
```

### CSV Reports
- `benchmark_tempi.csv` - Execution times per task
- `final_comparison_report.csv` - Main comparison

Columns in comparison:
```
Instance,T1,T2,T3,T4,Gap,Status
knapsack_data_10.json,100,98,95,97,3.00%,⚠️ Good
...
```

### HTML Report
- `report.html` - Interactive visualization
  - Solution comparison charts
  - Gap analysis
  - Status indicators
  - Execution statistics

**Open in any web browser**

### Log File
- `pipeline.log` - Detailed execution log
  - Task start/end times
  - Error messages
  - Warning messages
  - Performance metrics

**Grep for errors:**
```bash
grep ERROR outputs/run_*/pipeline.log
grep TIMEOUT outputs/run_*/pipeline.log
```

---

## File Naming Conventions

### Instances
- `knapsack_data_N.json` - N items
- `knapsack_data_N_hard.json` - N items, harder variant
- `supplier_cover_instance.json` - Alternative problem format

### Output Runs
- `run_YYYYMMDD_HHMMSS/` - Timestamp format
  - `YYYY` = 4-digit year
  - `MM` = 2-digit month
  - `DD` = 2-digit day
  - `HH` = 2-digit hour (24-hour)
  - `MM` = 2-digit minute
  - `SS` = 2-digit second

### Task Outputs
- `risultati_taskN.txt` - Italian: "results_taskN.txt"
- `risultati_task1.txt` - Results from Task 1
- `risultati_task2_qubo.txt` - Results from Task 2 (QUBO)
- `risultati_task3_qiskit.txt` - Results from Task 3 (Qiskit)
- `risultati_task4_dimod.txt` - Results from Task 4 (Dimod)

---

## Moving Forward

### If You Need to Reorganize Again

```bash
# Move all Python files to src/
mv *.py src/

# Move input data
mkdir -p input
mv knapsack_data*.json supplier_cover*.json input/

# Create outputs directory
mkdir outputs

# Update config.py with correct paths (already done)
# All imports will still work!
```

### Adding New Tasks

1. Create `src/knapsack_newapproach.py`
2. Implement `solve_knapsack_newapproach_batch(input_folder, output_file)`
3. Add to `pipeline.py` task list
4. Update `analyze_results.py` to parse results

### Customizing Output

Edit `analyze_results.py`:
```python
def generate_html_report(output_dir, all_jsons, report_rows):
    # Customize HTML generation
    # Add your own styling/charts
```

---

## Common Issues & Solutions

### Issue: ModuleNotFoundError: No module named 'config'

**Cause:** Running from wrong directory

**Solution:**
```bash
# Always run from project root
cd /home/locode/Personale/QML/pyhtonTest
uv run src/pipeline.py
```

### Issue: FileNotFoundError: [Errno 2] No such file or directory: 'input/...'

**Cause:** `INPUT_DIR` misconfigured in `src/config.py`

**Solution:**
```python
# Check in src/config.py
INPUT_DIR = os.path.join(PROJECT_ROOT, "input")  # ✅ Correct

# NOT this:
INPUT_DIR = os.path.join(BASE_DIR, "Input")      # ❌ Wrong
```

### Issue: Outputs appearing in wrong location

**Cause:** `OUTPUT_BASE_DIR` misconfigured

**Solution:**
```python
# Check in src/config.py
OUTPUT_BASE_DIR = os.path.join(PROJECT_ROOT, "outputs")  # ✅ Correct
```

---

## Summary

| What          | Where            | Access                            |
| ------------- | ---------------- | --------------------------------- |
| Source Code   | `src/`           | All together, easy to modify      |
| Input Data    | `input/`         | Configured in `src/config.py`     |
| Outputs       | `outputs/run_*/` | Timestamped, organized by run     |
| Configuration | `src/config.py`  | Change 68 params, no code editing |
| Documentation | Root directory   | README.md, QUICKSTART.md, etc.    |

**Golden Rule:** Run from project root, all paths are relative and work automatically! ✅
