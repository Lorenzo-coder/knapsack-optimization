"""
Configuration settings for Knapsack Optimization Pipeline.
Centralized configuration for all hardcoded values.
"""

import os

# Project directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)  # Parent directory of src/
INPUT_DIR = os.path.join(PROJECT_ROOT, "input")
OUTPUT_BASE_DIR = os.path.join(PROJECT_ROOT, "outputs")

# Input/Output file patterns
INPUT_FILE_PATTERN = "knapsack_data*.json"
SUPPLIER_INSTANCE = "supplier_cover_instance.json"

# Task output files
TASK1_OUTPUT = "risultati_task1.txt"
TASK2_OUTPUT = "risultati_task2_qubo.txt"
TASK3_OUTPUT = "risultati_task3_qiskit.txt"
TASK4_OUTPUT = "risultati_task4_dimod.txt"
BENCHMARK_OUTPUT = "benchmark_tempi.csv"
REPORT_OUTPUT = "final_comparison_report.csv"
LOG_FILE = "pipeline.log"

# Optimization parameters
# QUBO penalty coefficient multiplier
QUBO_PENALTY_MULTIPLIER = 2.0

# Qiskit parameters
QISKIT_TIMEOUT_SECONDS = 120  # Increased for QAOA convergence (was 30)
QISKIT_MAX_INSTANCE_SIZE = 10  # Max number of items for Qiskit

# In config.py, aggiungi:
GUROBI_SKIP_LARGE_INSTANCES = True
GUROBI_MAX_INSTANCE_SIZE = 100  # Skip istanze > 100 items due to the free license limit

# QAOA parameters
MAX_ITER_QAOA = 100  # Added MAX_ITER_QAOA for better control over QAOA optimization (was hardcoded in knapsack_qiskit_eigen.py)

# Dimod parameters
DIMOD_TIMEOUT_SECONDS = 120
DIMOD_SKIP_LARGE_INSTANCES = True
DIMOD_LARGE_INSTANCE_THRESHOLD = 10000  # Skip instances with size >= this

# Dimod annealing parameters
DIMOD_NUM_READS = 100
DIMOD_NUM_RUNS = 10

# Memory management
ENABLE_GARBAGE_COLLECTION = True
MEMORY_CHECK_INTERVAL = 5  # Check memory every N iterations

# Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_TO_FILE = True
LOG_TO_CONSOLE = True

# Report parsing
RESULTS_FILE_PATTERN = "risultati_task*.txt"
REPORT_SECTION_SEPARATOR = "FILE: "

# Error handling
CONTINUE_ON_ERROR = True
DETAILED_ERROR_LOGS = True

# Performance tuning
PARALLEL_PROCESSING = False  # Set to True for concurrent task execution
MAX_WORKERS = 4  # Number of parallel workers if enabled

# Testing/Development
DEBUG_MODE = False
SKIP_LARGE_INSTANCES = True
