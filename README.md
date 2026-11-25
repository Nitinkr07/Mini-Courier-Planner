# Mini-Courier Planner: Algorithmic Route & Load Optimization System

**Course:** Design & Analysis of Algorithms (`ETCCDA302`)  
**Programme:** B.Tech Computer Science & Engineering  
**Submitted By:** Nitin Kumar (Roll No: 2501010041)  
**Faculty:** Dr. Shweta Agarwal  

---

## 1. Overview
**Mini-Courier Planner** is an integrated Python prototype that simulates an intelligent logistics dispatch engine. Given a set of pending parcels with varying weights, priority values, delivery deadlines, and a weighted city road network, the system:
1. **Prioritizes** parcels using a stable divide-and-conquer sorting algorithm.
2. **Optimizes** vehicle capacity utilization using Dynamic Programming.
3. **Computes** shortest road paths and approximates an efficient multi-stop delivery tour using graph and heuristic algorithms.
4. **Benchmarks** execution runtime across scaling input sizes.

---

## 2. Algorithmic Architecture

| Pipeline Stage | Algorithm Used | Time Complexity | Space Complexity | Role in System |
| :--- | :--- | :--- | :--- | :--- |
| **Parcel Prioritization** | **Merge Sort** | $O(N \log N)$ | $O(N)$ | Orders parcels by earliest deadline (ASC) and priority value (DESC) while preserving relative order on ties. |
| **Vehicle Packing** | **0/1 Knapsack (DP)** | $O(N \cdot W)$ | $O(N \cdot W)$ | Selects the maximum-value subset of non-divisible parcels within weight capacity $W$. |
| **Point-to-Point Routing** | **Dijkstra's Algorithm** | $O((V + E) \log V)$ | $O(V + E)$ | Finds exact shortest road distances from the current stop to all candidate destinations. |
| **Multi-Stop Tour** | **Nearest-Neighbor TSP** | $O(K^2)$ *(for $K$ stops)* | $O(K)$ | Greedily constructs a closed delivery loop starting and ending at `"Hub"`. |

---

## 3. Repository Structure

```text
Mini-Courier-Planner/
├── README.md                    # Project documentation and setup instructions
├── mini_courier_planner.py      # Complete modular implementation (Phases 1–4)
└── results/                     # Execution evidence & charts
    ├── console_trace_1.png      # Output trace Part 1 (Merge Sort & 0/1 Knapsack DP table)
    ├── console_trace_2.png      # Output trace Part 2 (Dijkstra Route & Benchmark table)
    └── runtime_comparison.png   # Scaling performance plot (N = 10 to 2500)