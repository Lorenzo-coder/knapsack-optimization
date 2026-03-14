# Architecture Documentation

## System Overview

```
┌─────────────────────────────────────────────────────────┐
│         Knapsack Optimization Pipeline                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Input: JSON Instances (input/ directory)         │   │
│  └──────────────────────────────────────────────────┘   │
│                        ↓                                 │
│  ┌──────────────────────────────────────────────────┐   │
│  │ src/pipeline.py (Main Orchestrator)              │   │
│  │  • Load config from src/config.py                │   │
│  │  • Setup logging                                 │   │
│  │  • Create outputs/run_YYYYMMDD_HHMMSS/          │   │
│  │  • Run tasks sequentially                        │   │
│  │  • Generate report                               │   │
│  └──────────────────────────────────────────────────┘   │
│         ↙        ↓         ↓        ↘                   │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                   │
│  │Task1 │ │Task2 │ │Task3 │ │Task4 │                   │
│  │Exact │ │QUBO  │ │Qiskit│ │Dimod │                   │
│  └──────┘ └──────┘ └──────┘ └──────┘                   │
│         ↘        ↓         ↓        ↙                   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ src/analyze_results.py (Reporter)                │   │
│  │  • Parse all result files                        │   │
│  │  • Compare solutions                             │   │
│  │  • Generate CSV report                           │   │
│  │  • Generate HTML report                          │   │
│  └──────────────────────────────────────────────────┘   │
│                        ↓                                 │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Output: outputs/run_YYYYMMDD_HHMMSS/             │   │
│  │  • risultati_task1.txt                           │   │
│  │  • risultati_task2_qubo.txt                      │   │
│  │  • risultati_task3_qiskit.txt                    │   │
│  │  • risultati_task4_dimod.txt                     │   │
│  │  • benchmark_tempi.csv                           │   │
│  │  • final_comparison_report.csv                   │   │
│  │  • report.html                                   │   │
│  │  • pipeline.log                                  │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
pyhtonTest/
├── src/                          # All Python source code
│   ├── pipeline.py               # Main entry point
│   ├── config.py                 # 68 configuration parameters
│   ├── utils.py                  # Shared utilities
│   ├── knapsack_solver.py        # Task 1 implementation
│   ├── knapsack_solver_qubo.py   # Task 2 implementation
│   ├── knapsack_qiskit_eigen.py  # Task 3 implementation
│   ├── knapsack_dimod.py         # Task 4 implementation
│   ├── analyze_results.py        # Report generation
│   └── __pycache__/              # Python compiled cache
│
├── input/                        # Input data (lowercase 'input')
│   ├── knapsack_data_6.json
│   ├── knapsack_data_10.json
│   ├── knapsack_data_20.json
│   ├── knapsack_data_50.json
│   ├── knapsack_data_100.json
│   ├── knapsack_data_1000.json
│   ├── knapsack_data_10000.json
│   ├── knapsack_data_1000_hard.json
│   └── supplier_cover_instance.json
│
├── outputs/                      # Auto-generated output runs
│   ├── run_20260314_220406/
│   │   ├── risultati_task1.txt
│   │   ├── risultati_task2_qubo.txt
│   │   ├── risultati_task3_qiskit.txt
│   │   ├── risultati_task4_dimod.txt
│   │   ├── benchmark_tempi.csv
│   │   ├── final_comparison_report.csv
│   │   ├── report.html
│   │   └── pipeline.log
│   └── run_20260314_222727/
│       └── ...
│
├── uv.lock                       # Dependency lock file
├── pyproject.toml               # Project metadata (if present)
├── README.md                    # This project's overview
├── QUICKSTART.md                # Quick start guide
├── ARCHITECTURE.md              # This file
├── QKnapsack.pdf               # Problem specification
└── ...other docs...
```

---

## Module Dependency Graph

```
pipeline.py (entry point)
├── imports config.py
├── imports utils.py
│   ├── logging
│   ├── json validation
│   ├── timeout management (signal.SIGALRM)
│   └── error categorization
├── imports knapsack_solver.py (Task 1)
│   ├── imports config.py
│   ├── imports utils.py
│   └── depends on: pyomo.environ (Gurobi)
├── imports knapsack_solver_qubo.py (Task 2)
│   ├── imports config.py
│   ├── imports utils.py
│   └── depends on: pyomo.environ (Gurobi)
├── imports knapsack_qiskit_eigen.py (Task 3)
│   ├── imports config.py
│   ├── imports utils.py
│   └── depends on: qiskit_*, qiskit_algorithms, qiskit_optimization
├── imports knapsack_dimod.py (Task 4)
│   ├── imports config.py
│   ├── imports utils.py
│   └── depends on: dimod, neal
└── imports analyze_results.py (Reporter)
    ├── imports config.py (for OUTPUT_BASE_DIR)
    └── depends on: pandas, csv, re
```

---

## Execution Flow

```
1. User runs: cd /{path}/pyhtonTest && uv run src/pipeline.py

2. pipeline.py::run_full_pipeline():
   a) Load configuration from src/config.py
   b) Create output directory: outputs/run_YYYYMMDD_HHMMSS/
   c) Setup logging (file + console)
   
   For each task in [Task1, Task2, Task3, Task4]:
     i)   Time the task execution
     ii)  Call task function with (INPUT_DIR, output_file_path)
     iii) Catch exceptions (TimeoutError, MemoryError, ImportError, generic)
     iv)  Log results to benchmark list
     v)   Continue or abort based on CONTINUE_ON_ERROR
   
   d) Call analyzer(output_dir)
   e) Save benchmark CSV to outputs/run_*/benchmark_tempi.csv
   f) Print execution summary
   g) Force exit via sys.exit(0)

3. analyze_results.py::generate_comparison_report(output_dir):
   a) Parse all result files (Task 1, 2, 3, 4)
   b) Extract instance names and solution values
   c) Calculate gaps and status
   d) Generate final_comparison_report.csv
   e) Generate report.html with styling
```

---

## Configuration System (src/config.py)

```
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # /src
PROJECT_ROOT = os.path.dirname(BASE_DIR)               # /
INPUT_DIR = os.path.join(PROJECT_ROOT, "input")        # /input
OUTPUT_BASE_DIR = os.path.join(PROJECT_ROOT, "outputs")# /outputs
```

### Configuration Categories

1. **Directory Paths**

   - `INPUT_DIR`: Where JSON instances are loaded
   - `OUTPUT_BASE_DIR`: Where run folders are created
2. **Task Behavior**

   - `QISKIT_TIMEOUT_SECONDS`: 120
   - `DIMOD_TIMEOUT_SECONDS`: 120
   - Size limits for each solver
3. **Optimization Parameters**

   - `QUBO_PENALTY_MULTIPLIER`: 2.0
   - `DIMOD_NUM_READS`: 100
   - `MAX_ITER_QAOA`: 100
4. **Error Handling**

   - `CONTINUE_ON_ERROR`: True (continue if a task fails)
   - `DETAILED_ERROR_LOGS`: True
5. **Logging**

   - `LOG_LEVEL`: INFO
   - `LOG_TO_FILE`: True
   - `LOG_TO_CONSOLE`: True

---

## Data Flow Details

### Input Phase

```
JSON File Format (input/knapsack_data_10.json):
{
  "sets": {"P": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]},
  "parameters": {
    "b": 50,           # Knapsack capacity
    "C": {             # Item values
      "1": 10, "2": 20, ...
    },
    "a": {             # Item weights
      "1": 5, "2": 8, ...
    }
  }
}

↓ load_and_validate_instance(filepath)
  • Check JSON validity
  • Validate required keys
  • Check parameter types
  • Return Dict or None

↓ Used by all 4 tasks
```

### Processing Phase (Per Task)

**Task 1 (Exact):**

```
Instance → Pyomo Binary Model
    ↓
Define objective: maximize sum(C[i] * x[i])
Define constraint: sum(a[i] * x[i]) <= b
    ↓
Gurobi Solver
    ↓
Optimal solution found (or timeout)
```

**Task 2 (QUBO):**

```
Instance → Pyomo Model
    ↓
Convert constraint to penalty:
  Objective = sum(C[i]*x[i]) - PENALTY * (sum(a[i]*x[i]) - b)²
    ↓
Gurobi Solver (unconstrained QP)
    ↓
Solution (may violate capacity)
```

**Task 3 (Qiskit):**

```
Instance → Knapsack Application (Qiskit)
    ↓
Try: QAOA + StatevectorSampler (120s timeout)
    ↓
If timeout/fail: Try CPLEX optimizer
    ↓
If no CPLEX: Use greedy heuristic
    ↓
Solution
```

**Task 4 (Dimod):**

```
Instance → QUBO Matrix (Dimod)
    ↓
For 10 runs:
  Neal Simulated Annealing (120s timeout)
      ↓
  Find best among 10 runs
```

### Output Phase

```
All task output files:
  risultati_task1.txt
  risultati_task2_qubo.txt
  risultati_task3_qiskit.txt
  risultati_task4_dimod.txt

↓ analyze_results.py

Parse each file and extract:
  - Instance name
  - Solution value
  - Execution status

↓ Generate reports:
  - final_comparison_report.csv
  - report.html
```

---

## Task Implementations

### Task 1: knapsack_solver.py

**Function:** `solve_knapsack_batch(input_folder, output_file)`

```python
1. Iterate through all JSON files in input_folder
2. For each instance:
   a) Load and validate
   b) Build Pyomo model (binary variables, capacity constraint)
   c) Solve with Gurobi
   d) Extract optimal value
   e) Write to output_file
```

**Key Config Parameters:**

- `GUROBI_MAX_INSTANCE_SIZE`: Skip if > 100 items
- `INPUT_DIR`: Source of JSON files

---

### Task 2: knapsack_solver_qubo.py

**Function:** `solve_knapsack_qubo_batch(input_folder, output_file, penalty_multiplier)`

```python
1. Iterate through all JSON files in input_folder
2. For each instance:
   a) Load and validate
   b) Convert to QUBO with penalty method
   c) Penalty = QUBO_PENALTY_MULTIPLIER * max(values)
   d) Solve with Gurobi
   e) Extract solution value
   f) Write to output_file
```

**Key Config Parameters:**

- `QUBO_PENALTY_MULTIPLIER`: 2.0 (adjust for better solutions)
- `GUROBI_SKIP_LARGE_INSTANCES`: True
- `GUROBI_MAX_INSTANCE_SIZE`: 100

---

### Task 3: knapsack_qiskit_eigen.py

**Function:** `solve_knapsack_qiskit_batch(input_folder, output_file)`

**Fallback Chain:**

1. **Level 1:** QAOA with StatevectorSampler (120s timeout)

   - Most accurate for small instances
   - Often times out on instances > 10 items
2. **Level 2:** CPLEX Optimizer (if available)

   - Exact solver from IBM
   - Only works if CPLEX installed
3. **Level 3:** Greedy Heuristic (always available)

   - Selects items by value-to-weight ratio
   - Guaranteed feasible solution

```python
for instance in instances:
    try:
        # Try QAOA
        result = qaoa_solver.solve(qp)
    except (TimeoutError, ImportError, Exception):
        if CPLEX_AVAILABLE:
            try:
                result = cplex_solver.solve(qp)
            except:
                result = greedy_knapsack_solver(values, weights, capacity)
        else:
            result = greedy_knapsack_solver(values, weights, capacity)
```

**Key Config Parameters:**

- `QISKIT_TIMEOUT_SECONDS`: 120
- `QISKIT_MAX_INSTANCE_SIZE`: 10
- `MAX_ITER_QAOA`: 100

---

### Task 4: knapsack_dimod.py

**Function:** `solve_knapsack_dimod_batch(input_folder, output_file)`

```python
1. Iterate through all JSON files in input_folder
2. For each instance (if <= DIMOD_LARGE_INSTANCE_THRESHOLD):
   a) Load and validate
   b) For 10 independent runs:
      i)   Convert to QUBO
      ii)  Sample with Neal Simulated Annealing
      iii) Get best solution
   c) Save best among 10 runs
   d) Write to output_file
```

**Key Config Parameters:**

- `DIMOD_NUM_RUNS`: 10 (independent runs)
- `DIMOD_NUM_READS`: 100 (reads per run)
- `DIMOD_TIMEOUT_SECONDS`: 120
- `DIMOD_LARGE_INSTANCE_THRESHOLD`: 10000

---

## Error Handling

### Exception Hierarchy

```
TimeoutError (custom)
  → Raised by timeout() context manager
  → Category: TIMEOUT

MemoryError
  → Insufficient RAM
  → Category: MEMORY

ImportError
  → Missing dependencies
  → Category: DEPENDENCY

KeyError, ValueError
  → Invalid data
  → Category: INVALID_DATA

Generic Exception
  → Unknown
  → Category: UNKNOWN
```

### Timeout Mechanism

```python
from utils import timeout

with timeout(QISKIT_TIMEOUT_SECONDS):
    # Long-running code
    result = qaoa_solver.solve(qp)
    # If exceeds timeout, raises TimeoutError
```

Uses Unix signal `SIGALRM` to interrupt execution.

---

## Running from src/ Directory

When running `uv run src/pipeline.py` from the project root:

1. Python's working directory is `/{path}/pyhtonTest/`
2. Imports in `src/pipeline.py`:
   - `from config import ...` → Loads `src/config.py`
   - `from utils import ...` → Loads `src/utils.py`
   - `from knapsack_solver import ...` → Loads `src/knapsack_solver.py`
3. `src/config.py` constructs paths relative to `PROJECT_ROOT`:
   - `INPUT_DIR = os.path.join(PROJECT_ROOT, "input")`
   - `OUTPUT_BASE_DIR = os.path.join(PROJECT_ROOT, "outputs")`
4. All tasks find input files in `/input/` ✅
5. All outputs save to `/outputs/run_*/` ✅

**Key:** Don't run from inside `src/` directory. Always run from project root.

```
Task 1 (Exact):
  Instance → Pyomo Model → Gurobi Solver → Optimal Solution

Task 2 (QUBO):
  Instance → QUBO with Slack → Pyomo Model → Gurobi Solver → Solution

Task 3 (Qiskit):
  Instance → QuadraticProgram → QAOA → Quantum Simulator → Heuristic Solution

Task 4 (Dimod):
  Instance → BQM → Simulated Annealing → Heuristic Solution
```

### 3. Output Phase

```
Result Files (risultati_task*.txt)
    ↓
parse_results_file(filepath)
    ├── Split by "FILE:" markers
    ├── Extract values/weights
    ├── Extract unique solutions count
    └── Return: Dict[filename] → {value, weight, capacity, unique_runs}
    ↓
generate_comparison_report(output_dir)
    ├── Parse all 4 task results
    ├── Calculate gaps
    ├── Generate CSV report
    └── Print console summary
```

---

## Configuration Architecture

```
config.py (Single Source of Truth)
├── Directories
│   ├── BASE_DIR
│   ├── INPUT_DIR
│   └── OUTPUT_BASE_DIR
├── Task Parameters
│   ├── QUBO_PENALTY_MULTIPLIER
│   ├── QISKIT_* (timeout, max size)
│   └── DIMOD_* (timeout, reads, threshold)
├── Logging Config
│   ├── LOG_LEVEL
│   ├── LOG_FORMAT
│   └── LOG_TO_*
└── Error Handling
    ├── CONTINUE_ON_ERROR
    └── DETAILED_ERROR_LOGS
```

**Usage Pattern:**

```python
from config import PARAMETER_NAME
# No hardcoding needed!
```

---

## Error Handling Architecture

```
Exception Hierarchy:

Exception
├── TimeoutError (Custom)
│   └── Operations exceeding time limit
├── MemoryError (Built-in)
│   └── Insufficient memory
├── ImportError (Built-in)
│   └── Missing dependencies
├── KeyError (Built-in)
│   └── Invalid data structure
└── Exception (Generic)
    └── Other runtime errors
```

**Error Processing Flow:**

```python
try:
    solve_task(input, output)
except TimeoutError as e:
    category = "TIMEOUT"
    logger.error(f"[TIMEOUT] Task: {e}")
except MemoryError as e:
    category = "MEMORY"
    logger.error(f"[MEMORY] Task: {e}")
except ImportError as e:
    category = "DEPENDENCY"
    logger.error(f"[DEPENDENCY] Task: {e}")
except Exception as e:
    category = "UNKNOWN"
    logger.error(f"[UNKNOWN] Task: {e}", exc_info=True)
```

---

## Logging Architecture

```
Logger: KnapsackPipeline
├── Console Handler
│   └── Streams to stdout (real-time feedback)
└── File Handler
    └── Streams to run_YYYYMMDD_HHMMSS/pipeline.log (permanent record)

Both handlers use same format:
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

**Example Output:**

```
2025-03-14 15:39:34,123 - KnapsackPipeline - INFO - Pipeline started at 2025-03-14 15:39:34.123456
2025-03-14 15:39:34,456 - KnapsackPipeline - INFO - Output directory: run_20250314_153934
2025-03-14 15:39:35,789 - KnapsackPipeline - INFO - Task 1 completed in 1.33s
```

---

## Validation Architecture

```
JSON Instance Validation Pipeline:

1. File Existence Check
   └── If missing → log warning, skip

2. JSON Parsing
   └── If invalid → log warning, skip

3. Structure Validation
   ├── Required keys: "sets", "parameters"
   ├── Nested keys: "P", "b", "C", "a"
   └── If missing → log warning, skip

4. Type Validation
   ├── Check b is numeric and positive
   ├── Check C, A are dicts
   └── If invalid → log warning, skip

5. Data Quality Validation
   ├── P list not empty
   ├── C, A have entries for all items
   └── If invalid → log warning, skip

Result: Valid Dict or None
```

---

## Performance Optimization

### Memory Management

```python
# Enabled by config
if ENABLE_GARBAGE_COLLECTION:
    gc.collect()  # After each instance
```

### Timeout Protection

```python
# Context manager with signal
with timeout(QISKIT_TIMEOUT_SECONDS):
    result = solver.solve(qp)
    # Auto-cleanup on exit
```

### Instance Size Filtering

```python
# Skip instances exceeding thresholds
if len(P) > QISKIT_MAX_INSTANCE_SIZE:
    logger.warning(f"Skipped (too large)")
    continue
```

---

## Extensibility Points

### Adding New Tasks

```python
# 1. Add to pipeline.py
from new_solver import solve_new_batch as task5
tasks = [
    # ... existing tasks ...
    ("Task 5 - New Method", task5, "risultati_task5_new.txt"),
]

# 2. Create new_solver.py following existing pattern:
def solve_new_batch(input_folder: str, output_file: str) -> None:
    """Docstring with Args section"""
    from config import NEW_PARAM
    from utils import load_and_validate_instance
  
    # Implementation...

# 3. Update analyze_results.py to parse new file
# 4. Update config.py with new parameters
```

### Customizing Logging

```python
# In config.py
LOG_LEVEL = "DEBUG"  # More verbose
LOG_FORMAT = "%(asctime)s - %(filename)s:%(lineno)d - %(message)s"
```

### Tuning Parameters

```python
# In config.py (no code changes needed!)
QUBO_PENALTY_MULTIPLIER = 5.0  # Stricter constraint
QISKIT_MAX_INSTANCE_SIZE = 20  # Larger instances
DIMOD_NUM_READS = 200  # More samples
```

---

## Concurrency Considerations

**Current Implementation**: Sequential execution

- Task 1 → Task 2 → Task 3 → Task 4

**Future Enhancement**: Parallel execution

```python
# To enable in config.py:
PARALLEL_PROCESSING = True
MAX_WORKERS = 4  # Run up to 4 tasks in parallel

# Would require:
# 1. ThreadPoolExecutor or ProcessPoolExecutor
# 2. Thread-safe logging
# 3. Lock-based output file writing
```

---

## Testing Strategy

```
Unit Tests (hypothetical):
├── test_config.py
│   └── Verify all config vars exist and are correct type
├── test_utils.py
│   ├── Test load_and_validate_instance()
│   ├── Test timeout context manager
│   └── Test error formatting
├── test_tasks.py
│   ├── Test each task with small instance
│   └── Test error handling
└── test_integration.py
    └── Run full pipeline on test data

Integration Tests:
├── Small instance (6 items)
├── Medium instance (100 items)
└── Large instance (1000 items) [Task 1 & 2 only]
```

---

## Deployment Considerations

### Production Setup

```bash
# 1. Install dependencies
uv pip install -r requirements.txt

# 2. Configure for production
# Edit config.py:
# - CONTINUE_ON_ERROR = False  (Fail fast)
# - DEBUG_MODE = False
# - LOG_LEVEL = "WARNING"

# 3. Run with monitoring
python -u pipeline.py > pipeline.out 2>&1 &
tail -f run_*/pipeline.log
```

### Monitoring

```bash
# Check memory usage
watch -n 5 'ps aux | grep pipeline'

# Monitor file output
find run_* -name "*.txt" -exec wc -l {} +

# Track benchmark progress
tail -f run_*/benchmark_tempi.csv
```

---

## Security Considerations

1. **Path Traversal**: Validate all input file paths

   - ✅ Only read from `INPUT_DIR`
   - ✅ Only write to `output_dir`
2. **Code Injection**: No `eval()` or `exec()`

   - ✅ All inputs parsed safely with JSON schema
3. **Denial of Service**: Timeout protection

   - ✅ `QISKIT_TIMEOUT_SECONDS`
   - ✅ `DIMOD_TIMEOUT_SECONDS`
   - ✅ Instance size limits
4. **Configuration**: No secrets in code

   - ✅ All parameters in `config.py`
   - ✅ Can move to environment variables if needed

---

## Version Compatibility

- **Python**: 3.8+
- **Pyomo**: 6.0+
- **Gurobi**: 10.0+
- **Qiskit**: 0.43+
- **Dimod**: 0.12+

See `pyproject.toml` for full dependency list.

---

**Last Updated**: March 2026
**Architecture Version**: 2.0
