"""
Task 3: Quantum simulation with Qiskit.
Uses QAOA (Quantum Approximate Optimization Algorithm) with simulators.
"""

import os
import logging
from config import INPUT_DIR, QISKIT_TIMEOUT_SECONDS, QISKIT_MAX_INSTANCE_SIZE, MAX_ITER_QAOA
from utils import load_and_validate_instance, timeout

try:
    from qiskit.primitives import StatevectorSampler
    from qiskit_algorithms import QAOA
    from qiskit_algorithms.optimizers import COBYLA
    from qiskit_optimization.algorithms import MinimumEigenOptimizer, CplexOptimizer
    from qiskit_optimization.applications import Knapsack
    QAOA_AVAILABLE = True
    CPLEX_AVAILABLE = True
except ImportError:
    try:
        # Try without CPLEX
        QAOA_AVAILABLE = False
        CPLEX_AVAILABLE = False
        from qiskit_optimization.algorithms import GroverOptimizer
    except ImportError:
        # Final fallback: use a simple greedy heuristic
        QAOA_AVAILABLE = False
        CPLEX_AVAILABLE = False

logger = logging.getLogger(__name__)


def greedy_knapsack_solver(values: list, weights: list, capacity: float) -> dict:
    """
    Simple greedy heuristic for knapsack problem (fallback when optimizers fail).
    
    Args:
        values: Item values
        weights: Item weights  
        capacity: Knapsack capacity
        
    Returns:
        Dictionary with solution info
    """
    n = len(values)
    # Calculate value-to-weight ratio
    items_with_ratio = [(i, values[i] / weights[i] if weights[i] > 0 else 0, values[i], weights[i]) 
                        for i in range(n)]
    # Sort by ratio descending
    items_with_ratio.sort(key=lambda x: x[1], reverse=True)
    
    selected = []
    total_weight = 0
    total_value = 0
    
    # Greedily add items
    for idx, ratio, value, weight in items_with_ratio:
        if total_weight + weight <= capacity:
            selected.append(idx)
            total_weight += weight
            total_value += value
    
    # Convert indices to binary array
    x = [1 if i in selected else 0 for i in range(n)]
    
    return {
        'x': x,
        'value': total_value,
        'weight': total_weight,
        'feasible': total_weight <= capacity
    }



def solve_knapsack_qiskit_batch(input_folder: str, output_file: str) -> None:
    """
    Solve knapsack instances using Qiskit QAOA (or local solver fallback).
    
    Args:
        input_folder: Directory containing JSON knapsack instances
        output_file: Path to output file for results
    """
    with open(output_file, 'w') as out_f:
        out_f.write("REPORT RISULTATI - TASK 3 (QISKIT SIMULATION)\n")
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
            
            # Skip large instances for performance
            if len(P) > QISKIT_MAX_INSTANCE_SIZE:
                logger.warning(f"Skipped {filename}: Instance too large (>{QISKIT_MAX_INSTANCE_SIZE} items)")
                print(f"Skipped {filename}: Instance too large (>{QISKIT_MAX_INSTANCE_SIZE} items)")
                continue

            params = data["parameters"]
            b = params["b"]
            C = params["C"]
            A = params["a"]

            try:
                # Extract values and weights in order of P
                values = [C[i] for i in P]
                weights = [A[i] for i in P]
                
                # Attempt to use QAOA with timeout
                if QAOA_AVAILABLE:
                    with timeout(QISKIT_TIMEOUT_SECONDS):
                        # Build Knapsack problem using Qiskit built-in application
                        knapsack = Knapsack(values=values, weights=weights, max_weight=b)
                        qp = knapsack.to_quadratic_program()
                        
                        # Configure QAOA with StatevectorSampler (modern approach)
                        sampler = StatevectorSampler()
                        optimizer = COBYLA(maxiter=MAX_ITER_QAOA)
                        qaoa = QAOA(sampler=sampler, optimizer=optimizer, reps=2)
                        
                        # Solve directly without QUBO conversion (more stable)
                        solver = MinimumEigenOptimizer(qaoa)
                        result = solver.solve(qp)
                        
                        # Extract solution - get first n_items values (skip slack variables)
                        n_items = len(P)
                        selected_indices = [int(x) for x in result.x[:n_items]]
                        selected = [P[idx] for idx, x in enumerate(selected_indices) if x == 1]
                        val = sum(C[i] for i in selected)
                        weight = sum(A[i] for i in selected)

                        out_f.write(f"\nFILE: {filename}\n")
                        out_f.write(f"  Selected items: {selected}\n")
                        out_f.write(f"  Valore Totale: {val}\n")
                        out_f.write(f"  Peso Totale: {weight} / {b}\n")
                        out_f.write(f"  Method: Qiskit QAOA (Quantum Simulation)\n")
                        out_f.write("-" * 40 + "\n")
                        
                        logger.info(f"Processed: {filename} -> Value: {val}")
                        print(f"Processed: {filename}")
                else:
                    # Use classical solver via Qiskit or greedy fallback
                    if CPLEX_AVAILABLE:
                        try:
                            solver = CplexOptimizer()
                            knapsack = Knapsack(values=values, weights=weights, max_weight=b)
                            qp = knapsack.to_quadratic_program()
                            result = solver.solve(qp)

                            selected_indices = [int(x) for x in result.x]
                            selected = [P[idx] for idx, x in enumerate(selected_indices) if x == 1]
                            val = sum(C[i] for i in selected)
                            weight = sum(A[i] for i in selected)

                            out_f.write(f"\nFILE: {filename}\n")
                            out_f.write(f"  Selected items: {selected}\n")
                            out_f.write(f"  Valore Totale: {val}\n")
                            out_f.write(f"  Peso Totale: {weight} / {b}\n")
                            out_f.write(f"  Method: Qiskit CPLEX (Classical Solver)\n")
                            out_f.write("-" * 40 + "\n")
                            logger.info(f"Processed (CPLEX): {filename} -> Value: {val}")
                            print(f"Processed (CPLEX): {filename}")
                        except Exception as cplex_e:
                            logger.warning(f"CPLEX solver failed, using greedy heuristic: {cplex_e}")
                            result_dict = greedy_knapsack_solver(values, weights, b)
                            selected = [P[idx] for idx, x in enumerate(result_dict['x']) if x == 1]
                            
                            out_f.write(f"\nFILE: {filename}\n")
                            out_f.write(f"  Selected items: {selected}\n")
                            out_f.write(f"  Valore Totale: {result_dict['value']}\n")
                            out_f.write(f"  Peso Totale: {result_dict['weight']} / {b}\n")
                            out_f.write(f"  Method: Greedy Heuristic (Fallback)\n")
                            out_f.write("-" * 40 + "\n")
                            logger.info(f"Processed (greedy): {filename} -> Value: {result_dict['value']}")
                            print(f"Processed (greedy): {filename}")
                    else:
                        # Use pure greedy heuristic
                        result_dict = greedy_knapsack_solver(values, weights, b)
                        selected = [P[idx] for idx, x in enumerate(result_dict['x']) if x == 1]
                        
                        out_f.write(f"\nFILE: {filename}\n")
                        out_f.write(f"  Selected items: {selected}\n")
                        out_f.write(f"  Valore Totale: {result_dict['value']}\n")
                        out_f.write(f"  Peso Totale: {result_dict['weight']} / {b}\n")
                        out_f.write(f"  Method: Greedy Heuristic (Fallback)\n")
                        out_f.write("-" * 40 + "\n")
                        logger.info(f"Processed (fallback): {filename} -> Value: {result_dict['value']}")
                        print(f"Processed (fallback): {filename}")

            except TimeoutError:
                logger.warning(f"Timeout on {filename}: Skipped")
                print(f"⏱️  Timeout on {filename}: Skipped")
                out_f.write(f"\nFILE: {filename}\n")
                out_f.write(f"  Result: TIMEOUT after {QISKIT_TIMEOUT_SECONDS}s\n")
                out_f.write("-" * 40 + "\n")
                    
            except Exception as e:
                logger.error(f"Error solving {filename}: {e}")
                print(f"Error on {filename}: {e}")
                # Try greedy solver as ultimate fallback
                try:
                    result_dict = greedy_knapsack_solver(values, weights, b)
                    selected = [P[idx] for idx, x in enumerate(result_dict['x']) if x == 1]

                    out_f.write(f"\nFILE: {filename}\n")
                    out_f.write(f"  Selected items: {selected}\n")
                    out_f.write(f"  Valore Totale: {result_dict['value']}\n")
                    out_f.write(f"  Peso Totale: {result_dict['weight']} / {b}\n")
                    out_f.write(f"  Method: Greedy Heuristic (Emergency Fallback)\n")
                    out_f.write("-" * 40 + "\n")
                    logger.info(f"Processed (emergency greedy): {filename} -> Value: {result_dict['value']}")
                    print(f"Processed (emergency greedy): {filename}")
                except Exception as greedy_e:
                    logger.error(f"Even greedy solver failed on {filename}: {greedy_e}")
                    out_f.write(f"\nFILE: {filename}\n")
                    out_f.write(f"  Result: FAILED - {str(greedy_e)[:100]}\n")
                    out_f.write("-" * 40 + "\n")

    logger.info(f"Task 3 completed. Results saved to: {output_file}")
    print(f"\nTask 3 completed. Results saved to: {output_file}")


if __name__ == "__main__":
    solve_knapsack_qiskit_batch(INPUT_DIR, "risultati_task3_qiskit.txt")