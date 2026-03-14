# Final Technical Report: Combinatorial Optimization of the Knapsack Problem

## 1. Executive Summary and Methodology

This report provides a comprehensive analysis of the 0-1 Knapsack Problem through various computational lenses: Classical Mathematical Programming, Quadratic Unconstrained Binary Optimization (QUBO), and Quantum-Inspired Heuristics. The goal was to assess the trade-offs between mathematical optimality and computational scalability.

### Task 1: Deterministic MILP Approach

We implemented the primary benchmark using the **Pyomo** algebraic modeling language, utilizing the **Gurobi/HiGHS** solvers. This approach models the problem as a Mixed-Integer Linear Program (MILP), leveraging the *Branch and Bound* algorithm. It provides the "Ground Truth" by guaranteeing the global optimum.

### Task 2: QUBO Transformation for Quantum Readiness

In preparation for quantum architectures, we reformulated the constrained optimization problem into a QUBO form:

* **Constraint Penalty**: We converted the inequality constraint ($\le b$) into an equality using **binary slack variables**.
* **Lagrange Formulation**: A squared penalty term was added to the objective function:
   $H = -\sum c_i x_i + \lambda (\sum a_i x_i + \text{slack} - b)^2$.
   This transforms the problem into an unconstrained energy minimization task.

### Task 3: Quantum Simulation (Qiskit)

Using the **Qiskit Optimization** stack, we mapped the problem into an Ising Hamiltonian. Due to recent updates in Qiskit 1.x and the instability of variational modules (QAOA) in certain environments, we utilized a high-fidelity **Eigensolver** simulation to identify the state of minimum energy (Ground State), effectively simulating an ideal quantum processor.

### Task 4: Quantum-Inspired Simulated Annealing (Dimod)

We utilized the **D-Wave Dimod** framework and the `neal` sampler to execute **Simulated Annealing**. This heuristic simulates the physical cooling of a system to "tunnel" through energy barriers and find a low-energy configuration corresponding to a near-optimal solution.

---

## 2. Comparative Analysis of Results

The following table summarizes the performance across different problem sizes:


| Instance                 | Task 1 (Exact) | Task 2 (QUBO) | Task 4 (Heuristic) | Reliability          |
| :----------------------- | :------------: | :-----------: | :----------------: | :------------------- |
| `knapsack_data.json`     |    **15.0**    |   **15.0**    |      **15.0**      | 100%                 |
| `knapsack_data_10.json`  |   **372.0**    |   **372.0**   |       271.0        | Sub-optimal          |
| `knapsack_data_100.json` |   **3647.0**   |  **3647.0**   |       3034.0       | Approx. 83% Accuracy |

### Analysis of Convergence

The results show that Task 2 (solved classically) perfectly matches Task 1. This is a critical validation step, proving that our **Lagrange penalty formulation and slack variable integration** are mathematically sound. The sub-optimality in Task 4 indicates that while the model is correct, the heuristic search for the global minimum becomes significantly harder as the problem size (and the number of local minima) increases.

---

## 3. Benchmarking and Runtime Performance

Data from `benchmark_tempi.csv` reveals the computational cost of shifting paradigms:

* **Classical Linear Solver (0.16s)**: Highly optimized for these instances. It remains the fastest method for small to medium problems.
* **Exact QUBO Solver (150.47s)**: This massive overhead demonstrates that while QUBO is necessary for quantum hardware, it is inherently inefficient for classical CPUs. The quadratic expansion of the constraint increases the number of interactions exponentially.
* **Simulated Annealing (9.16s)**: Task 4 is notably faster than the exact QUBO solver. This confirms that for quadratic models, **probabilistic sampling** is much more scalable than exact matrix diagonalization or traditional quadratic programming.

---

## 4. Evaluation of Stochasticity and Repeated Runs

A core requirement was the analysis of repeated runs within the stochastic framework of Task 4.

* **Findings**: For the `knapsack_data_10.json` instance, our logs indicate **"10 unique solutions found over 10 runs"**.
* **Interpretation**: This high level of variability suggests a very "rugged" energy landscape. Unlike the deterministic Task 1, Simulated Annealing explores a probabilistic space where many different item combinations yield similar energy levels. The solver rarely converges to the exact same point, emphasizing that in quantum-inspired optimization, multiple "reads" are required to increase the probability of capturing the true global optimum.

---

## 5. Final Reflection: Exact vs. Heuristic Optimization

This study highlights a fundamental duality in modern optimization:

1. **Exact Optimization (Tasks 1 & 2)**: Offers mathematical certainty and serves as the ultimate validation tool. However, the transformation into QUBO (Task 2) artificially complicates the problem for classical hardware, showing that QUBO is a specific "language" meant for Quantum Annealers rather than traditional computers.
2. **Quantum-Inspired Heuristics (Task 4)**: Represents the practical frontier for large-scale NP-Hard problems. While it sacrifices the guarantee of optimality, it provides a linear-like scalability in time that classical exact methods cannot maintain as $N$ grows.

**Conclusion**: The success of the transition from classical to quantum optimization relies heavily on the **Penalty Parameter ($\lambda$)**. Tuning this parameter is essential: a value too low leads to constraint violations (overfilled knapsack), while a value too high "flattens" the profit objective, leading the solver to ignore high-value items in favor of simply satisfying the weight limit.
