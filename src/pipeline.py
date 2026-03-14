"""
Main pipeline for Knapsack Optimization.
Orchestrates execution of 4 different solving approaches:
1. Classical exact solution (Pyomo + Gurobi)
2. QUBO formulation (Pyomo + Gurobi)
3. Quantum simulation (Qiskit QAOA)
4. Quantum-inspired annealing (Dimod)
"""

import time
import os
import sys
import pandas as pd
from datetime import datetime

from config import INPUT_DIR, CONTINUE_ON_ERROR, OUTPUT_BASE_DIR
from utils import setup_logging, get_memory_usage_mb, format_error_message

try:
    from knapsack_solver import solve_knapsack_batch as task1
    from knapsack_solver_qubo import solve_knapsack_qubo_batch as task2
    from knapsack_qiskit_eigen import solve_knapsack_qiskit_batch as task3
    from knapsack_dimod import solve_knapsack_dimod_batch as task4
    from analyze_results import generate_comparison_report as analyzer
except ImportError as e:
    print(f"ERROR: Import failed: {e}")
    print("Make sure all .py files are in the same directory.")
    sys.exit(1)

def run_full_pipeline():
    """Execute the complete optimization pipeline with all 4 tasks."""
    # Create unique output directory with timestamp in outputs/ folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(OUTPUT_BASE_DIR, f"run_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    
    # Setup logging
    logger = setup_logging(output_dir)
    logger.info(f"Pipeline started at {datetime.now()}")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Input directory: {INPUT_DIR}")
    
    start_mem = get_memory_usage_mb()
    benchmarks = []

    print(f"--- Knapsack Optimization Pipeline: {datetime.now()} ---")
    print(f"--- Output folder: {output_dir} ---")
    
    tasks = [
        ("Task 1 - Classico Esatto", task1, "risultati_task1.txt"),
        ("Task 2 - QUBO (Gurobi/HiGHS)", task2, "risultati_task2_qubo.txt"),
        ("Task 3 - Qiskit Simulation", task3, "risultati_task3_qiskit.txt"),
        ("Task 4 - Dimod Annealing", task4, "risultati_task4_dimod.txt"),
    ]

    for name, func, out_file in tasks:
        # Build full output path within unique output folder
        full_out_path = os.path.join(output_dir, out_file)
        
        logger.info(f"Starting {name}...")
        print(f"\nExecuting {name}...")
        start = time.perf_counter()
        
        try:
            func(INPUT_DIR, full_out_path)
            end = time.perf_counter()
            duration = round(end - start, 2)
            end_mem = get_memory_usage_mb()
            
            benchmarks.append({
                "Task": name, 
                "Duration (s)": duration, 
                "Memory (MB)": round(end_mem - start_mem, 4), 
                "Status": "Success",
                "Output_File": full_out_path
            })
            
            logger.info(f"{name} completed in {duration}s")
            print(f"Completed in {duration} seconds.")
            
        except TimeoutError as e:
            error_msg = format_error_message(name, e)
            logger.error(error_msg)
            print(f"ERROR: {error_msg}")
            benchmarks.append({
                "Task": name, 
                "Duration (s)": 0, 
                "Memory (MB)": 0, 
                "Status": error_msg
            })
            
            if not CONTINUE_ON_ERROR:
                logger.critical(f"Pipeline stopped due to {name}")
                raise
                
        except MemoryError as e:
            error_msg = format_error_message(name, e)
            logger.error(error_msg)
            print(f"ERROR: {error_msg}")
            benchmarks.append({
                "Task": name, 
                "Duration (s)": 0, 
                "Memory (MB)": 0, 
                "Status": error_msg
            })
            
        except ImportError as e:
            error_msg = format_error_message(name, e)
            logger.error(error_msg)
            print(f"ERROR: {error_msg}")
            benchmarks.append({
                "Task": name, 
                "Duration (s)": 0, 
                "Memory (MB)": 0, 
                "Status": error_msg
            })
            
        except Exception as e:
            error_msg = format_error_message(name, e)
            logger.error(error_msg, exc_info=True)
            print(f"ERROR: {error_msg}")
            benchmarks.append({
                "Task": name, 
                "Duration (s)": 0, 
                "Memory (MB)": 0, 
                "Status": error_msg
            })
            
            if not CONTINUE_ON_ERROR:
                logger.critical(f"Pipeline stopped due to {name}")
                raise

    # Generate final comparison report
    print("\n--- Generating Comparison Report ---")
    try:
        analyzer(output_dir)
        logger.info("Comparison report generated successfully")
        print("Report generated successfully.")
    except Exception as e:
        error_msg = f"Error generating report: {e}"
        logger.error(error_msg, exc_info=True)
        print(f"ERROR: {error_msg}")

    # Save global execution times in unique output folder
    df_bench = pd.DataFrame(benchmarks)
    benchmark_path = os.path.join(output_dir, "benchmark_tempi.csv")
    df_bench.to_csv(benchmark_path, index=False)
    
    print(f"\n{'='*70}")
    print(f"✅ PIPELINE COMPLETED SUCCESSFULLY")
    print(f"{'='*70}")
    print(f"📁 Results saved in: {output_dir}")
    print(f"{'='*70}")
    print(df_bench)
    print(f"{'='*70}\n")
    logger.info(f"Pipeline completed successfully. Results in: {output_dir}")
    
    # Final timing summary
    print(f"\n⏱️  EXECUTION SUMMARY:")
    total_time = df_bench[df_bench['Status'] == 'Success']['Duration (s)'].sum()
    print(f"   Total Time (Completed Tasks): {total_time:.2f}s")
    print(f"   Output Directory: {output_dir}\n")
    
    # Force exit to prevent hanging processes
    import sys
    sys.exit(0)


if __name__ == "__main__":
    run_full_pipeline()