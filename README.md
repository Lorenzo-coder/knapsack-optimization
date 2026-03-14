# Knapsack Optimization Pipeline

A comprehensive Python pipeline for solving the binary knapsack problem using four different optimization approaches:
1. **Classical exact solution** (Pyomo + Gurobi)
2. **QUBO formulation** (Pyomo + Gurobi)
3. **Quantum simulation** (Qiskit QAOA)
4. **Quantum-inspired annealing** (Dimod)

## Project Structure

```
knapsack-optimization/
├── src/                        # All source code
│   ├── pipeline.py             # Main orchestration script
│   ├── config.py               # Centralized configuration
│   ├── utils.py                # Shared utilities (logging, validation, timeouts)
│   ├── knapsack_solver.py      # Task 1: Classical exact
│   ├── knapsack_solver_qubo.py # Task 2: QUBO formulation
│   ├── knapsack_qiskit_eigen.py# Task 3: Qiskit quantum
│   ├── knapsack_dimod.py       # Task 4: Dimod annealing
│   └── analyze_results.py      # Result parsing and reporting
├── input/                      # JSON knapsack instances
│   ├── knapsack_data_6.json
│   ├── knapsack_data_10.json
│   ├── knapsack_data_20.json
│   ├── knapsack_data_50.json
│   ├── knapsack_data_100.json
│   ├── knapsack_data_1000.json
│   ├── knapsack_data_10000.json
│   └── ...
├── outputs/                    # Auto-generated output directories
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
├── uv.lock                     # Dependency lock file
└── README.md                   # This file
```

## Installation

### Prerequisites
- Python 3.8+
- `uv` package manager

### Setup

```bash
# Navigate to the project directory
cd /{path}/knapsack-optimization

# Install dependencies using uv
uv pip install \
    pyomo \
    gurobi \
    qiskit \
    qiskit-aer \
    qiskit-optimization \
    dimod \
    neal \
    pandas \
    psutil
```

**Optional:** Install Qiskit algorithms for enhanced quantum features
```bash
uv pip install qiskit-algorithms
```

## Configuration

All hardcoded values are centralized in `src/config.py`:

### Key Parameters

| Parameter                        | Default | Purpose                                              |
| -------------------------------- | ------- | ---------------------------------------------------- |
| `QUBO_PENALTY_MULTIPLIER`        | 2.0     | Penalty strength for constraint violations           |
| `QISKIT_TIMEOUT_SECONDS`         | 120     | Max time per instance for Qiskit                     |
| `QISKIT_MAX_INSTANCE_SIZE`       | 10      | Skip instances larger than this                      |
| `GUROBI_MAX_INSTANCE_SIZE`       | 100     | Skip instances larger than this (free license limit) |
| `DIMOD_NUM_READS`                | 100     | Annealing runs per instance                          |
| `DIMOD_TIMEOUT_SECONDS`          | 120     | Max time per instance for Dimod                      |
| `DIMOD_LARGE_INSTANCE_THRESHOLD` | 10000   | Skip instances with >= this items                    |
| `CONTINUE_ON_ERROR`              | True    | Continue pipeline on task failure                    |
| `LOG_LEVEL`                      | INFO    | Logging verbosity                                    |

Modify `src/config.py` to adjust behavior without changing task implementations.

## Usage

### Run Full Pipeline

```bash
cd /{path}/knapsack-optimization
uv run src/pipeline.py
```

This executes all 4 tasks sequentially and generates:
- Individual result files for each task
- Benchmark timing CSV
- Comparative analysis report (CSV + HTML)
- Unified log file

**Output location:** `outputs/run_YYYYMMDD_HHMMSS/`

### Output Files

| File                          | Purpose                            | Priority    |
| ----------------------------- | ---------------------------------- | ----------- |
| `final_comparison_report.csv` | Compare all solutions              | ✅ Primary   |
| `report.html`                 | Interactive visual report          | ✅ Primary   |
| `benchmark_tempi.csv`         | Execution times per task           | 📊 Secondary |
| `pipeline.log`                | Detailed execution logs            | 🔧 Debug     |
| `risultati_task1.txt`         | Classical optimal solutions        | 📌 Reference |
| `risultati_task2_qubo.txt`    | QUBO solutions                     | 📌 Reference |
| `risultati_task3_qiskit.txt`  | Quantum (Qiskit) solutions         | 📌 Reference |
| `risultati_task4_dimod.txt`   | Quantum-inspired (Dimod) solutions | 📌 Reference |

## Task Descriptions

### Task 1: Classical Exact Solution
- **Algorithm:** Branch & Bound (via Gurobi)
- **Guarantee:** Optimal solution
- **Time Complexity:** Variable (NP-hard)
- **Use Case:** Baseline and ground truth
- **Limitations:** Slow for instances > 100 items

### Task 2: QUBO Formulation
- **Algorithm:** Penalty method + Gurobi
- **Guarantee:** Not guaranteed optimal (due to penalty approximation)
- **Time Complexity:** Variable (converted to QP)
- **Use Case:** Understand penalty-based methods
- **Limitations:** Quality depends on penalty multiplier

### Task 3: Quantum Simulation (Qiskit)
- **Algorithm:** QAOA (Quantum Approximate Optimization Algorithm)
- **Fallback Chain:** QAOA → CPLEX → Greedy heuristic
- **Guarantee:** Heuristic solution
- **Timeout:** 120 seconds per instance
- **Use Case:** Explore quantum-inspired algorithms
- **Limitations:** Expensive for larger instances

### Task 4: Quantum-Inspired Annealing (Dimod)
- **Algorithm:** Simulated annealing (Neal sampler)
- **Runs:** 10 independent runs per instance
- **Guarantee:** Heuristic solution
- **Timeout:** 120 seconds per instance
- **Use Case:** Fast heuristic solutions
- **Limitations:** Quality depends on annealing parameters

### Run Individual Tasks

```bash
# Task 1: Classical exact
uv run knapsack_solver.py

# Task 2: QUBO
uv run knapsack_solver_qubo.py

# Task 3: Qiskit quantum
uv run knapsack_qiskit_eigen.py

# Task 4: Dimod annealing
uv run knapsack_dimod.py

# Generate comparison report
uv run analyze_results.py
```

## JSON Instance Format

Each knapsack instance must follow this structure:

```json
{
  "sets": {
    "P": ["1", "2", "3", "4"]
  },
  "parameters": {
    "b": 10,
    "C": {
      "1": 8,
      "2": 6,
      "3": 5,
      "4": 4
    },
    "a": {
      "1": 6,
      "2": 4,
      "3": 3,
      "4": 2
    }
  }
}
```

### Fields
- `sets.P`: List of item identifiers
- `parameters.b`: Knapsack capacity
- `parameters.C`: Item values/profits
- `parameters.a`: Item weights

## Output Files

### Result Files (in `run_YYYYMMDD_HHMMSS/`)

**risultati_task1.txt** - Exact classical solution
- Optimal value
- Selected items
- Feasibility guaranteed

**risultati_task2_qubo.txt** - QUBO solution
- QUBO-formulated solution
- May be suboptimal (depends on penalty coefficient)
- Feasibility not guaranteed

**risultati_task3_qiskit.txt** - Quantum simulation results
- QAOA solution (or fallback Slsqp)
- Heuristic (variable across runs)
- May timeout on large instances

**risultati_task4_dimod.txt** - Annealing results
- Simulated annealing solution
- Shows solution diversity (unique solutions found)
- Heuristic (variable across runs)

### Benchmark Report

**benchmark_tempi.csv** - Execution metrics
```
Task,Duration (s),Memory (MB),Status
Task 1 - Classico Esatto,2.15,45.32,Success
Task 2 - QUBO (Gurobi/HiGHS),1.89,42.15,Success
...
```

**final_comparison_report.csv** - Quality comparison
```
JSON_Instance,T1_Value,T2_Value,T3_Value,T4_Value,Gap_T1_T4 (%)
knapsack_data_10.json,42.0,42.0,40.0,38.0,9.52
...
```

## Architecture

### Error Handling

The pipeline implements differentiated error handling:

```python
try:
    func(input_dir, output_file)
except TimeoutError:
    # Operation exceeded time limit
except MemoryError:
    # Insufficient memory
except ImportError:
    # Missing dependency
except Exception:
    # Other runtime errors
```

### Timeout Management

Qiskit and Dimod tasks use context managers to enforce timeouts:

```python
with timeout(QISKIT_TIMEOUT_SECONDS):
    # Automatic timeout after N seconds
```

### Logging

Dual logging to console and file:

```
2025-03-14 15:39:34,123 - KnapsackPipeline - INFO - Task 1 completed in 2.15s
```

## Performance Considerations

### Instance Sizes

| Size           | Task 1   | Task 2   | Task 3      | Task 4   |
| -------------- | -------- | -------- | ----------- | -------- |
| ≤10 items      | ✅ Fast   | ✅ Fast   | ✅ Fast      | ✅ Fast   |
| 10-50 items    | ✅ Fast   | ✅ Fast   | ✅ Slow      | ✅ Medium |
| 50-100 items   | ✅ Medium | ✅ Medium | ⚠️ Very Slow | ✅ Medium |
| 100-1000 items | ✅ Medium | ✅ Medium | ❌ Skip      | ⚠️ Slow   |
| >1000 items    | ⚠️ Slow   | ⚠️ Slow   | ❌ Skip      | ❌ Skip   |

**Qiskit** has lower instance size limits due to quantum circuit complexity.
**Dimod** can handle larger instances but may timeout with very large ones.

### Memory Usage

Track memory via benchmark CSV or log file:

```bash
grep "Memory (MB)" run_*/benchmark_tempi.csv
```

## Troubleshooting

### "No module named 'qiskit_algorithms'"
```bash
uv pip install qiskit-algorithms
```

### "Gurobi not found"
```bash
uv pip install gurobi
# Or use fallback solver: appsi_highs
```

### Timeout on large instances
Adjust in `config.py`:
```python
QISKIT_TIMEOUT_SECONDS = 60  # Increase timeout
QISKIT_MAX_INSTANCE_SIZE = 20  # Increase max size
```

### Import errors in pipeline
Ensure all task files are in the same directory:
```bash
ls -la *.py | grep knapsack
```

## Understanding Results

### Why Different Solutions?

**Task 1** (Exact): Always optimal ✅
**Task 2** (QUBO): Depends on penalty coefficient ⚠️
**Task 3** (Qiskit): Heuristic, varies by run 🎲
**Task 4** (Dimod): Heuristic, varies by run 🎲

The quality gap shows how far Tasks 3-4 are from the optimal Task 1 solution.

### Quality Gap

```
Gap (%) = (T1_Value - T4_Value) / T1_Value * 100
```

- 0% = Task 4 found optimal
- <5% = Excellent heuristic
- 5-15% = Good heuristic
- >15% = Poor heuristic or wrong parameters

## References

- Kochol, P. (2007). A Polynomial Algorithm for the Knapsack Problem Based on a New Decomposition Theorem
- Qiskit Documentation: https://qiskit.org
- Dimod Documentation: https://docs.ocean.dwavesys.com/en/stable/docs_dimod/

## License

Educational project - Master-level Python course

---

**Last Updated**: March 2026
**Version**: 2.0 (Refactored with config centralization)
