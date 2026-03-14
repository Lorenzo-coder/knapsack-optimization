import json
import os
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_aer.primitives import Sampler
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA

def solve_knapsack_qiskit_batch(input_folder, output_file):
    with open(output_file, 'w') as out_f:
        out_f.write("REPORT RISULTATI - TASK 3 (QISKIT STABLE)\n")
        out_f.write("="*40 + "\n")

        files = [f for f in os.listdir(input_folder) if f.endswith('.json')]
        
        for filename in sorted(files):
            filepath = os.path.join(input_folder, filename)
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            P = data["sets"]["P"]
            # Restiamo su istanze molto piccole per evitare timeout o errori di memoria
            if len(P) > 10: 
                print(f"Saltato {filename}: Istanze > 10 elementi sono troppo pesanti per QAOA locale.")
                continue

            params = data["parameters"]
            b = params.get("b")
            C = params.get("C", {})
            A = params.get("a", {})

            # Costruzione del problema
            qp = QuadraticProgram(name=filename)
            for i in P:
                qp.binary_var(name=f'x_{i}')

            qp.maximize(linear={f'x_{i}': C[i] for i in P})
            qp.linear_constraint(linear={f'x_{i}': A[i] for i in P}, sense="<=", rhs=b)

            try:
                # Setup QAOA
                # Usiamo Sampler di Aer che è più stabile con qiskit-algorithms
                sampler = Sampler()
                optimizer = COBYLA()
                qaoa = QAOA(sampler=sampler, optimizer=optimizer, reps=1)
                
                # MinimumEigenOptimizer si occupa di gestire la conversione QUBO e le slack variables
                meo = MinimumEigenOptimizer(qaoa)
                result = meo.solve(qp)

                # Estrazione risultati
                # x è un array con i valori delle variabili decisionali
                selected = [i for idx, i in enumerate(P) if result.x[idx] > 0.5]
                val = sum(C[i] for i in selected)
                weight = sum(A[i] for i in selected)

                out_f.write(f"\nFILE: {filename}\n")
                out_f.write(f"  Elementi selezionati: {selected}\n")
                out_f.write(f"  Valore Totale: {val}\n")
                out_f.write(f"  Peso Totale: {weight} / {b}\n")
                out_f.write("-" * 20 + "\n")
                print(f"Elaborato (Qiskit): {filename}")

            except Exception as e:
                # Se c'è un errore di compatibilità, lo stampiamo ma non blocchiamo il ciclo
                print(f"Errore tecnico su {filename}: {e}")

if __name__ == "__main__":
    input_directory = "/home/locode/Personale/QML/pyhtonTest/Input" 
    output_filename = "risultati_task3_qiskit.txt"
    solve_knapsack_qiskit_batch(input_directory, output_filename)