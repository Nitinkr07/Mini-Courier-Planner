import heapq
import random
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple


# ==============================================================================
# PHASE 1: DATA STRUCTURES
# ==============================================================================
@dataclass
class Parcel:
    parcel_id: str
    destination: str
    weight: int      # in kg (integer required for 0/1 DP table indexing)
    value: int       # priority score / revenue
    deadline: int    # hours remaining until due


class DeliveryGraph:
    """Weighted undirected graph using an adjacency list."""

    def __init__(self) -> None:
        self.adj: Dict[str, List[Tuple[str, float]]] = {}

    def add_edge(self, u: str, v: str, weight: float) -> None:
        self.adj.setdefault(u, []).append((v, weight))
        self.adj.setdefault(v, []).append((u, weight))


# ==============================================================================
# PHASE 2: PACKAGE PRIORITIZATION (MERGE SORT) & BOX FILLING (0/1 KNAPSACK DP)
# ==============================================================================
def merge_sort_parcels(parcels: List[Parcel]) -> List[Parcel]:
    """
    Sorts parcels primarily by earliest deadline (ascending),
    and secondarily by highest value/priority (descending).
    Time Complexity: O(N log N) | Space Complexity: O(N)
    """
    if len(parcels) <= 1:
        return parcels

    mid = len(parcels) // 2
    left = merge_sort_parcels(parcels[:mid])
    right = merge_sort_parcels(parcels[mid:])

    return _merge(left, right)


def _merge(left: List[Parcel], right: List[Parcel]) -> List[Parcel]:
    merged: List[Parcel] = []
    i = j = 0

    while i < len(left) and j < len(right):
        # Prioritize smaller deadline; tie-break with higher value
        if (left[i].deadline, -left[i].value) <= (right[j].deadline, -right[j].value):
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def knapsack_01_packing(
    parcels: List[Parcel], capacity: int, return_table: bool = False
) -> Tuple[int, List[Parcel], List[List[int]]]:
    """
    0/1 Knapsack Dynamic Programming to select optimal parcels within capacity.
    Time Complexity: O(N * W) | Space Complexity: O(N * W)
    """
    n = len(parcels)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    # Build DP table bottom-up
    for i in range(1, n + 1):
        w_i = parcels[i - 1].weight
        v_i = parcels[i - 1].value
        for w in range(capacity + 1):
            if w_i <= w:
                dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - w_i] + v_i)
            else:
                dp[i][w] = dp[i - 1][w]

    # Backtrack to find selected parcels
    selected: List[Parcel] = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected.append(parcels[i - 1])
            w -= parcels[i - 1].weight

    selected.reverse()
    return dp[n][capacity], selected, (dp if return_table else [])


# ==============================================================================
# PHASE 3: ROUTE MAKER (DIJKSTRA'S ALGORITHM + NEAREST-NEIGHBOR TSP)
# ==============================================================================
def dijkstra_shortest_paths(
    graph: DeliveryGraph, start: str
) -> Tuple[Dict[str, float], Dict[str, str]]:
    """
    Computes shortest distances from `start` to all reachable nodes.
    Time Complexity: O((V + E) log V) | Space Complexity: O(V + E)
    """
    distances: Dict[str, float] = {node: float("inf") for node in graph.adj}
    previous: Dict[str, str] = {}
    distances[start] = 0.0

    min_heap: List[Tuple[float, str]] = [(0.0, start)]

    while min_heap:
        curr_dist, u = heapq.heappop(min_heap)

        if curr_dist > distances[u]:
            continue

        for v, weight in graph.adj.get(u, []):
            new_dist = curr_dist + weight
            if new_dist < distances[v]:
                distances[v] = new_dist
                previous[v] = u
                heapq.heappush(min_heap, (new_dist, v))

    return distances, previous


def reconstruct_path(previous: Dict[str, str], start: str, target: str) -> List[str]:
    path = []
    curr = target
    while curr != start:
        path.append(curr)
        curr = previous.get(curr)
        if curr is None:
            return []
    path.append(start)
    return path[::-1]


def nearest_neighbor_tsp(
    graph: DeliveryGraph, hub: str, stops: List[str]
) -> Tuple[List[str], float, List[Tuple[str, str, float, List[str]]]]:
    """
    Approximates the shortest delivery tour starting and ending at `hub`
    using Dijkstra distances between unvisited stops.
    Time Complexity: O(K * (V + E) log V + K^2)
    """
    unvisited = set(stops)
    unvisited.discard(hub)

    current = hub
    tour = [hub]
    total_distance = 0.0
    leg_details: List[Tuple[str, str, float, List[str]]] = []

    while unvisited:
        dists, prev = dijkstra_shortest_paths(graph, current)
        # Pick closest unvisited delivery stop
        next_stop = min(unvisited, key=lambda node: dists[node])
        leg_dist = dists[next_stop]
        leg_path = reconstruct_path(prev, current, next_stop)

        total_distance += leg_dist
        tour.append(next_stop)
        leg_details.append((current, next_stop, leg_dist, leg_path))

        unvisited.remove(next_stop)
        current = next_stop

    # Return to Hub
    dists, prev = dijkstra_shortest_paths(graph, current)
    return_dist = dists[hub]
    return_path = reconstruct_path(prev, current, hub)
    total_distance += return_dist
    tour.append(hub)
    leg_details.append((current, hub, return_dist, return_path))

    return tour, total_distance, leg_details


# ==============================================================================
# PHASE 4: BENCHMARKING & DATASET GENERATOR
# ==============================================================================
def generate_synthetic_data(
    num_parcels: int, num_nodes: int, seed: int = 42
) -> Tuple[List[Parcel], DeliveryGraph]:
    rng = random.Random(seed)
    nodes = ["Hub"] + [f"Loc_{i}" for i in range(1, num_nodes)]
    graph = DeliveryGraph()

    # Ensure connected backbone (spanning tree)
    for i in range(1, len(nodes)):
        parent = nodes[rng.randint(0, i - 1)]
        graph.add_edge(parent, nodes[i], round(rng.uniform(2.0, 15.0), 1))

    # Add extra random cross-edges
    for _ in range(num_nodes):
        u, v = rng.sample(nodes, 2)
        graph.add_edge(u, v, round(rng.uniform(3.0, 20.0), 1))

    parcels = [
        Parcel(
            parcel_id=f"PKG-{i:04d}",
            destination=rng.choice(nodes[1:]),
            weight=rng.randint(1, 15),
            value=rng.randint(10, 100),
            deadline=rng.randint(1, 24),
        )
        for i in range(1, num_parcels + 1)
    ]
    return parcels, graph


def run_benchmark() -> None:
    sizes = [10, 100, 500, 1000, 2500]
    capacity = 100
    print("\n" + "=" * 72)
    print("PHASE 4: PERFORMANCE BENCHMARKING ACROSS INPUT SIZES")
    print("=" * 72)
    print(f"{'Parcels':<10} | {'Nodes':<8} | {'Sort (ms)':<12} | {'Knapsack (ms)':<15} | {'Routing (ms)':<12}")
    print("-" * 72)

    sort_times, dp_times, route_times = [], [], []

    for n in sizes:
        num_nodes = max(6, min(n // 5, 150))
        parcels, graph = generate_synthetic_data(n, num_nodes)

        t0 = time.perf_counter()
        sorted_p = merge_sort_parcels(parcels)
        t1 = time.perf_counter()

        _, selected, _ = knapsack_01_packing(sorted_p, capacity)
        t2 = time.perf_counter()

        stops = list({p.destination for p in selected})
        nearest_neighbor_tsp(graph, "Hub", stops)
        t3 = time.perf_counter()

        s_ms = (t1 - t0) * 1000
        d_ms = (t2 - t1) * 1000
        r_ms = (t3 - t2) * 1000

        sort_times.append(s_ms)
        dp_times.append(d_ms)
        route_times.append(r_ms)

        print(f"{n:<10} | {num_nodes:<8} | {s_ms:<12.3f} | {d_ms:<15.3f} | {r_ms:<12.3f}")

    # Optional: Generate runtime chart if matplotlib is installed
    try:
        import matplotlib.pyplot as plt

        plt.figure(figsize=(8, 5))
        plt.plot(sizes, sort_times, marker="o", label="Merge Sort O(N log N)")
        plt.plot(sizes, dp_times, marker="s", label="0/1 Knapsack DP O(N*W)")
        plt.plot(sizes, route_times, marker="^", label="Dijkstra + NN TSP")
        plt.title("Mini-Courier Planner: Runtime Scaling Analysis")
        plt.xlabel("Number of Parcels (N)")
        plt.ylabel("Execution Time (ms)")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.tight_layout()
        plt.savefig("runtime_comparison.png", dpi=150)
        print("\n[Saved runtime chart to 'runtime_comparison.png']")
    except ImportError:
        print("\n[Install matplotlib (`pip install matplotlib`) to auto-save runtime_comparison.png]")


# ==============================================================================
# DEMONSTRATION TRACE (SMALL DATASET WITH FULL DP TABLE & ROUTE OUTPUT)
# ==============================================================================
def run_demo() -> None:
    print("=" * 72)
    print("MINI-COURIER PLANNER: END-TO-END TRACE (CAPACITY = 15 kg)")
    print("=" * 72)

    sample_parcels = [
        Parcel("P101", "Sector_A", weight=6, value=50, deadline=4),
        Parcel("P102", "Sector_B", weight=5, value=40, deadline=2),
        Parcel("P103", "Sector_C", weight=4, value=35, deadline=2),
        Parcel("P104", "Sector_A", weight=7, value=60, deadline=6),
        Parcel("P105", "Sector_D", weight=3, value=25, deadline=3),
    ]

    city_graph = DeliveryGraph()
    city_graph.add_edge("Hub", "Sector_A", 4.0)
    city_graph.add_edge("Hub", "Sector_B", 2.5)
    city_graph.add_edge("Sector_A", "Sector_B", 3.0)
    city_graph.add_edge("Sector_A", "Sector_C", 5.0)
    city_graph.add_edge("Sector_B", "Sector_D", 6.0)
    city_graph.add_edge("Sector_C", "Sector_D", 2.0)

    # 1. Sort
    sorted_parcels = merge_sort_parcels(sample_parcels)
    print("\n[1] Prioritized Parcels (Merge Sort by Deadline ASC, Value DESC):")
    for p in sorted_parcels:
        print(f"  {p.parcel_id} -> {p.destination:<8} | Deadline: {p.deadline}h | Weight: {p.weight}kg | Value: {p.value}")

    # 2. Knapsack DP
    capacity = 15
    max_val, packed, dp_table = knapsack_01_packing(sorted_parcels, capacity, return_table=True)
    print(f"\n[2] 0/1 Knapsack Packing Plan (Max Value = {max_val}, Total Weight = {sum(p.weight for p in packed)}/{capacity} kg):")
    for p in packed:
        print(f"  SELECTED: {p.parcel_id} ({p.destination}, {p.weight}kg, Value {p.value})")

    print("\n    DP Table Snapshot (Rows: Items 0..N, Cols: Capacity 0..15):")
    for row in dp_table:
        print("   ", " ".join(f"{val:3d}" for val in row))

    # 3. Dijkstra + Nearest-Neighbor TSP
    unique_stops = list({p.destination for p in packed})
    tour, total_km, legs = nearest_neighbor_tsp(city_graph, "Hub", unique_stops)

    print("\n[3] Delivery Route Plan (Dijkstra + Nearest-Neighbor TSP):")
    for src, dst, dist, sub_path in legs:
        print(f"  {src} -> {dst} ({dist:.1f} km) via {' -> '.join(sub_path)}")
    print(f"\n  Final Delivery Sequence : {' -> '.join(tour)}")
    print(f"  Total Route Distance    : {total_km:.1f} km")


if __name__ == "__main__":
    run_demo()
    run_benchmark()