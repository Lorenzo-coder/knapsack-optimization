"""
Task 2: QUBO formulation using Pyomo + Gurobi.
Converts the standard knapsack problem into an unconstrained quadratic form
by penalizing capacity constraint violations.
"""

import pyomo.environ as pyo_env
import os
import math
import logging
from config import INPUT_DIR, QUBO_PENALTY_MULTIPLIER, GUROBI_SKIP_LARGE_INSTANCES, GUROBI_MAX_INSTANCE_SIZE
from utils import load_and_validate_instance

logger = logging.getLogger(__name__)


def solve_knapsack_qubo_batch(input_folder: str, output_file: str, 
                             penalty_multiplier: float = QUBO_PENALTY_MULTIPLIER) -> None:
    """
    Solve knapsack instances using QUBO formulation (Pyomo + Gurobi).
    
    Args:
        input_folder: Directory containing JSON knapsack instances
        output_file: Path to output file for results
        penalty_multiplier: Multiplier for penalty coefficient
    """
    with open(output_file, 'w') as out_f:
        out_f.write("REPORT RISULTATI - TASK 2 (QUBO-STYLE)\n")
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
            params = data["parameters"]
            b = params["b"]
            C = params["C"]
            A = params["a"]

            # Check instance size to avoid Gurobi license limits
            if GUROBI_SKIP_LARGE_INSTANCES and len(P) >= GUROBI_MAX_INSTANCE_SIZE:
                logger.warning(f"Skipped {filename}: Instance too large (>={GUROBI_MAX_INSTANCE_SIZE} items)")
                print(f"Skipped: {filename} (Gurobi size limit)")
                continue

            # Build QUBO model with slack variables
            model = pyo_env.ConcreteModel()
            model.P = pyo_env.Set(initialize=P)
            model.x = pyo_env.Var(model.P, domain=pyo_env.Binary)

            # Slack variables for capacity constraint encoding
            num_slack_bits = math.floor(math.log2(b)) + 1
            model.S_indices = pyo_env.RangeSet(0, num_slack_bits - 1)
            model.s = pyo_env.Var(model.S_indices, domain=pyo_env.Binary)

            # Penalty coefficient: higher value enforces capacity constraint more strictly
            penalty_coeff = max(C.values()) * penalty_multiplier

            # Objective: maximize value minus penalty for constraint violation
            obj_gain = sum(C[i] * model.x[i] for i in model.P)
            slack_sum = sum((2**k) * model.s[k] for k in model.S_indices)
            penalty_term = (sum(A[i] * model.x[i] for i in model.P) + slack_sum - b)**2

            model.obj = pyo_env.Objective(
                expr=obj_gain - penalty_coeff * penalty_term, 
                sense=pyo_env.maximize
            )

            # Solve with Gurobi
            try:
                solver = pyo_env.SolverFactory('gurobi')
                solver.solve(model, tee=False)

                selected = [i for i in model.P if pyo_env.value(model.x[i]) > 0.5]
                val = sum(C[i] for i in selected)
                weight = sum(A[i] for i in selected)
                feasible = "YES" if weight <= b else "NO"

                out_f.write(f"\nFILE: {filename}\n")
                out_f.write(f"  Selected items: {selected}\n")
                out_f.write(f"  Valore Totale: {val}\n")
                out_f.write(f"  Peso Totale: {weight} / {b}\n")
                out_f.write(f"  Feasible: {feasible}\n")
                out_f.write("-" * 40 + "\n")
                
                logger.info(f"Processed: {filename} -> Value: {val}, Feasible: {feasible}")
                print(f"Processed: {filename}")
                
            except Exception as e:
                logger.error(f"Error solving {filename}: {e}")
                print(f"Error solving {filename}: {e}")

    logger.info(f"Task 2 completed. Results saved to: {output_file}")
    print(f"\nTask 2 completed. Results saved to: {output_file}")


if __name__ == "__main__":
    solve_knapsack_qubo_batch(INPUT_DIR, "risultati_task2_qubo.txt")