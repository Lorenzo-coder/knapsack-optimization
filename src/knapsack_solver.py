"""
Task 1: Classical exact solution using Pyomo + Gurobi.
Solves the standard binary knapsack problem to proven optimality.
"""

import pyomo.environ as pyo_env
import os
import logging
from config import INPUT_DIR, GUROBI_MAX_INSTANCE_SIZE
from utils import load_and_validate_instance

logger = logging.getLogger(__name__)


def solve_knapsack_batch(input_folder: str, output_file: str) -> None:
    """
    Solve knapsack instances using exact optimization (Pyomo + Gurobi).
    
    Args:
        input_folder: Directory containing JSON knapsack instances
        output_file: Path to output file for results
    """
    with open(output_file, 'w') as out_f:
        out_f.write("REPORT RISULTATI - TASK 1 (CLASSICAL EXACT)\n")
        out_f.write("="*50 + "\n")

        files = [f for f in os.listdir(input_folder) if f.endswith('.json')]
        
        for filename in sorted(files):
            filepath = os.path.join(input_folder, filename)
            
            # Validate instance before solving
            data = load_and_validate_instance(filepath)
            if data is None:
                logger.warning(f"Skipped: {filename} (invalid structure)")
                print(f"Skipped: {filename} (invalid structure)")
                continue

            P = data["sets"]["P"]
            if len(P) > GUROBI_MAX_INSTANCE_SIZE:
                logger.warning(f"Skipped: {filename} (Gurobi size limit)")
                continue
            params = data["parameters"]
            b = params["b"]
            C = params["C"]
            A = params["a"]

            # Build Pyomo model
            model = pyo_env.ConcreteModel()
            model.P = pyo_env.Set(initialize=P)
            model.x = pyo_env.Var(model.P, domain=pyo_env.Binary)

            # Objective function: maximize total value
            model.obj = pyo_env.Objective(
                expr=sum(C[i] * model.x[i] for i in model.P), 
                sense=pyo_env.maximize
            )

            # Capacity constraint
            model.cap = pyo_env.Constraint(
                expr=sum(A[i] * model.x[i] for i in model.P) <= b
            )

            try:
                # Use Gurobi for exact optimization
                solver = pyo_env.SolverFactory('gurobi') 
                solver.solve(model, tee=False)
                
                # Extract results
                selected = [i for i in model.P if pyo_env.value(model.x[i]) > 0.5]
                val = pyo_env.value(model.obj)
                weight = sum(A[i] for i in selected)

                out_f.write(f"\nFILE: {filename}\n")
                out_f.write(f"  Selected items: {selected}\n")
                out_f.write(f"  Valore Totale: {val}\n")
                out_f.write(f"  Peso Totale: {weight} / {b}\n")
                out_f.write("-" * 40 + "\n")
                
                logger.info(f"Processed: {filename} -> Value: {val}")
                print(f"Processed: {filename}")
                
            except Exception as e:
                logger.error(f"Error solving {filename}: {e}")
                print(f"Error solving {filename}: {e}")

    logger.info(f"Task 1 completed. Results saved to: {output_file}")
    print(f"\nTask 1 completed. Results saved to: {output_file}")


if __name__ == "__main__":
    solve_knapsack_batch(INPUT_DIR, "risultati_task1.txt")