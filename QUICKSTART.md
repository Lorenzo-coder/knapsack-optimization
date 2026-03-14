# Quick Start Guide

## 30-Second Setup

```bash
cd /home/locode/Personale/QML/pyhtonTest

# Install all dependencies
uv pip install pyomo gurobi qiskit qiskit-aer qiskit-optimization qiskit-algorithms dimod neal pandas psutil

# Run the full pipeline
uv run src/pipeline.py
```

That's it! Results will be in `outputs/run_YYYYMMDD_HHMMSS/` directory.

---

## Output Files (What to Look At)

| File                          | Purpose                   | Most Important   |
| ----------------------------- | ------------------------- | ---------------- |
| `final_comparison_report.csv` | Compare solution quality  | ✅ YES            |
| `report.html`                 | Interactive visualization | ✅ YES            |
| `benchmark_tempi.csv`         | Execution times           | 📊 Maybe          |
| `pipeline.log`                | Debug information         | 🔧 If errors      |
| `risultati_task1.txt`         | Optimal solutions         | ✅ Reference      |
| `risultati_task4_dimod.txt`   | Heuristic solutions       | ⚠️ For comparison |

---

## Common Tasks

### View Latest Results

```bash
# View latest comparison report
tail outputs/run_*/final_comparison_report.csv

# Check execution times
cat outputs/run_*/benchmark_tempi.csv

# See errors (if any)
grep ERROR outputs/run_*/pipeline.log

# Open HTML report in browser
open outputs/run_*/report.html  # macOS
xdg-open outputs/run_*/report.html  # Linux
```

### Adjust Behavior (Without Editing Code)

Edit `src/config.py` before running:

```python
# Increase timeout for slower machines
QISKIT_TIMEOUT_SECONDS = 180  # was 120

# Allow larger instances
QISKIT_MAX_INSTANCE_SIZE = 20  # was 10

# More annealing runs = better quality (slower)
DIMOD_NUM_READS = 200  # was 100

# Stricter penalty for QUBO
QUBO_PENALTY_MULTIPLIER = 5.0  # was 2.0

# Skip very large instances
DIMOD_LARGE_INSTANCE_THRESHOLD = 5000  # was 10000
```

### Run Single Task

Individual tasks require more setup. Better to run full pipeline, or edit `pipeline.py` to skip tasks.

---

## Understanding the Results

### Solution Quality Gap

```
Optimal Value (Task 1)    = 100
Heuristic Value (Task 4)  = 95
Gap = (100-95)/100 = 5%
```

**Interpretation:**
- **0%** = Perfect! Heuristic found optimal
- **<5%** = Excellent quality
- **5-15%** = Good quality
- **>15%** = Poor quality or need parameter tuning

### Why Different Each Run?

Tasks 3 and 4 are **stochastic** (random):
- **Qiskit:** QAOA varies by initialization and sampler randomness
- **Dimod:** Simulated annealing uses randomness; Task 4 does 10 independent runs

Run multiple times to see variability.

### CSV Report Columns

| Column     | Meaning                            |
| ---------- | ---------------------------------- |
| `Instance` | Problem instance name              |
| `T1`       | Task 1 (exact) solution value      |
| `T2`       | Task 2 (QUBO) solution value       |
| `T3`       | Task 3 (Qiskit) solution value     |
| `T4`       | Task 4 (Dimod) best solution value |
| `Gap`      | (T1-T4)/T1 percentage gap          |
| `Status`   | ✅ Optimal, ⚠️ Good, ❌ Poor          |

---

## Troubleshooting

### Import Error: ModuleNotFoundError

```bash
# Run from project root, not from src/
cd /home/locode/Personale/QML/pyhtonTest
uv run src/pipeline.py  # ✅ Correct
```

### Task 3 (Qiskit) Timeout

Qiskit QAOA is expensive. If you see timeouts:
```python
# Increase timeout in src/config.py
QISKIT_TIMEOUT_SECONDS = 180  # was 120
```

### Task 2 (QUBO) Crashes

Gurobi free license has size limits. If crashes on large instances:
```python
# Reduce max instance size in src/config.py
GUROBI_MAX_INSTANCE_SIZE = 50  # was 100
```

### Memory Issues

Enable garbage collection in `src/config.py`:
```python
ENABLE_GARBAGE_COLLECTION = True  # Default is already True
```

### Missing Dependencies

```bash
# Reinstall all dependencies
uv pip install --force-reinstall \
    pyomo qiskit qiskit-aer qiskit-optimization \
    qiskit-algorithms dimod neal pandas psutil gurobi
```

---

## Next Steps

1. **Run the pipeline:** `uv run src/pipeline.py`
2. **Open HTML report:** `outputs/run_*/report.html`
3. **Analyze CSV:** View `final_comparison_report.csv` in Excel or similar
4. **Tune parameters:** Edit `src/config.py` and re-run
5. **Read documentation:** See `ARCHITECTURE.md` for deep dive**Task 1 is always the same** (deterministic)
**Task 2 depends on penalty coefficient**

### Reading the Report

```csv
JSON_Instance,T1_Value,T2_Value,T3_Value,T4_Value,T4_Unique_Runs,Gap_T1_T4 (%)
knapsack_data_10.json,42.0,42.0,40.0,38.0,3,9.52
```

- **T1_Value** (42.0) = Optimal
- **T4_Value** (38.0) = Best heuristic found
- **Gap** (9.52%) = How far off optimal
- **Unique_Runs** (3) = Solution diversity (high = unstable)

---

## Troubleshooting

### "No module named X"

```bash
# Install the missing module
uv pip install <module_name>

# Common ones:
uv pip install qiskit-algorithms  # For Qiskit QAOA
uv pip install gurobi              # For exact solver
```

### Timeout on Large Instances

```python
# In config.py - increase timeout
QISKIT_TIMEOUT_SECONDS = 120  # was 30
```

### Out of Memory

```python
# In config.py - skip large instances
DIMOD_SKIP_LARGE_INSTANCES = True
DIMOD_LARGE_INSTANCE_THRESHOLD = 1000  # Skip >1000 items
```

### Wrong Solutions

```python
# Adjust QUBO penalty (higher = stricter constraints)
QUBO_PENALTY_MULTIPLIER = 5.0  # was 2.0

# More annealing samples (slower but better)
DIMOD_NUM_READS = 500  # was 100
```

---

## File Structure

```
pyhtonTest/
├── config.py                    ← Edit this for configuration
├── pipeline.py                  ← Run this (main script)
├── knapsack_solver.py           (Task 1: Exact)
├── knapsack_solver_qubo.py      (Task 2: QUBO)
├── knapsack_qiskit_eigen.py     (Task 3: Quantum)
├── knapsack_dimod.py            (Task 4: Annealing)
├── analyze_results.py           (Report generation)
├── utils.py                     (Shared utilities)
├── Input/                       ← JSON instances
│   ├── knapsack_data_6.json
│   ├── knapsack_data_10.json
│   └── ...
├── run_20250314_153934/         ← Auto-generated output
│   ├── final_comparison_report.csv
│   ├── benchmark_tempi.csv
│   ├── pipeline.log
│   └── risultati_task*.txt
├── README.md                    (Full documentation)
└── config.py                    (Detailed configuration)
```

---

## Performance Tips

### Speed Up Processing

1. **Skip large instances**
   ```python
   QISKIT_MAX_INSTANCE_SIZE = 5    # Only small ones
   DIMOD_SKIP_LARGE_INSTANCES = True
   ```

2. **Reduce samples**
   ```python
   DIMOD_NUM_READS = 10  # Fast but lower quality
   ```

3. **Shorter timeouts**
   ```python
   QISKIT_TIMEOUT_SECONDS = 10
   ```

### Improve Quality

1. **More samples**
   ```python
   DIMOD_NUM_READS = 500  # Slower but better
   ```

2. **Stricter penalties**
   ```python
   QUBO_PENALTY_MULTIPLIER = 10.0
   ```

3. **Longer timeouts**
   ```python
   QISKIT_TIMEOUT_SECONDS = 120
   ```

---

## Next Steps

1. **First Run**: Run with defaults, check results
2. **Understand**: Read `final_comparison_report.csv`
3. **Tune**: Adjust parameters in `config.py` if needed
4. **Iterate**: Run again with new parameters
5. **Document**: Check `pipeline.log` for details

---

## Full Documentation

- 📖 **README.md** - Complete project documentation
- 🏗️ **ARCHITECTURE.md** - Technical design details
- 📝 **SUMMARY.md** - What was refactored and why

---

## Support

### Debug Mode

```python
# In config.py
DEBUG_MODE = True
LOG_LEVEL = "DEBUG"  # Maximum verbosity
```

### Check Logs

```bash
cat run_YYYYMMDD_HHMMSS/pipeline.log
```

### Check Results

```bash
cat run_YYYYMMDD_HHMMSS/final_comparison_report.csv
```

---

**Happy optimizing!** 🚀
