"""
Task 4: Quantum-inspired annealing solution using Dimod.
Uses simulated annealing to solve QUBO formulations of the knapsack problem.
Multiple runs to analyze solution variability.
"""

import os
import logging
from config import (
    INPUT_DIR, DIMOD_TIMEOUT_SECONDS, DIMOD_SKIP_LARGE_INSTANCES,
    DIMOD_LARGE_INSTANCE_THRESHOLD, DIMOD_NUM_READS
)
from utils import load_and_validate_instance, timeout

try:
    import dimod
    from neal import SimulatedAnnealingSampler
except ImportError as e:
    raise ImportError(f"Dimod or neal not installed: {e}")

logger = logging.getLogger(__name__)


def solve_knapsack_dimod_batch(input_folder: str, output_file: str) -> None:
    """
    Solve knapsack instances using Dimod simulated annealing.
    Performs multiple runs to analyze solution stability.
    
    Args:
        input_folder: Directory containing JSON knapsack instances
        output_file: Path to output file for results
    """
    sampler = SimulatedAnnealingSampler()

    with open(output_file, 'w') as out_f:
        out_f.write("REPORT RISULTATI - TASK 4 (DIMOD ANNEALING)\n")
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
            
            # Skip large instances for performance if configured
            if DIMOD_SKIP_LARGE_INSTANCES and len(P) >= DIMOD_LARGE_INSTANCE_THRESHOLD:
                logger.warning(f"Skipped {filename}: Instance too large (>={DIMOD_LARGE_INSTANCE_THRESHOLD} items)")
                print(f"Skipped {filename}: Instance too large (>={DIMOD_LARGE_INSTANCE_THRESHOLD} items)")
                continue

            params = data["parameters"]
            b = params["b"]
            C = params["C"]
            A = params["a"]

            # Build Binary Quadratic Model (QUBO)
            # Objective: minimize H = -sum(c_i * x_i) + lambda * (sum(a_i * x_i) - b)^2
            bqm = dimod.BinaryQuadraticModel(dimod.Vartype.BINARY)

            # Add objective terms (negative because dimod minimizes energy)
            for i in P:
                bqm.add_variable(i, -C[i])

            # Add capacity constraint with penalty
            penalty_coeff = max(C.values()) * 2
            bqm.add_linear_inequality_constraint(
                [(i, A[i]) for i in P],
                constant=-b,
                lagrange_multiplier=penalty_coeff,
                label='capacity'
            )

            try:
                # Run simulated annealing with timeout
                with timeout(DIMOD_TIMEOUT_SECONDS):
                    sampleset = sampler.sample(
                        bqm, 
                        num_reads=DIMOD_NUM_READS
                    )

                    # Extract best solution
                    best_sample = sampleset.first.sample
                    selected = [i for i in P if best_sample[i] > 0.5]
                    val = sum(C[i] for i in selected)
                    weight = sum(A[i] for i in selected)

                    # Count unique solutions
                    num_unique_solutions = len(sampleset.aggregate())

                    out_f.write(f"\nFILE: {filename}\n")
                    out_f.write(f"  Selected items: {selected}\n")
                    out_f.write(f"  Valore Totale: {val}\n")
                    out_f.write(f"  Peso Totale: {weight} / {b}\n")
                    out_f.write(f"  Best energy: {sampleset.first.energy:.2f}\n")
                    out_f.write(f"  Soluzioni uniche trovate su {DIMOD_NUM_READS} run: {num_unique_solutions}\n")
                    out_f.write("-" * 40 + "\n")
                    
                    logger.info(f"Processed: {filename} -> Value: {val}, Unique solutions: {num_unique_solutions}")
                    print(f"Processed: {filename}")

            except TimeoutError:
                logger.warning(f"Timeout on {filename}: Skipped")
                print(f"⏱️  Timeout on {filename}: Skipped")
                out_f.write(f"\nFILE: {filename}\n")
                out_f.write(f"  Result: TIMEOUT after {DIMOD_TIMEOUT_SECONDS}s\n")
                out_f.write("-" * 40 + "\n")
                
            except Exception as e:
                logger.error(f"Error solving {filename}: {e}")
                print(f"Error on {filename}: {e}")

    logger.info(f"Task 4 completed. Results saved to: {output_file}")
    print(f"\nTask 4 completed. Results saved to: {output_file}")


if __name__ == "__main__":
    solve_knapsack_dimod_batch(INPUT_DIR, "risultati_task4_dimod.txt")