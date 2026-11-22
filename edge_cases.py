"""Nạp Edge Cases độc lập từ CSV - không sửa 5 kịch bản SC01-SC05."""
import csv
from pathlib import Path
from graph import FlowGraph

ROOT = Path(__file__).resolve().parent / "tests" / "fixtures" / "edge_cases"

def read_cases():
    with (ROOT / "cases.csv").open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))

def load_case(case_id):
    if case_id not in {case["case_id"] for case in read_cases()}:
        raise ValueError("Khong co case: " + case_id)
    folder = ROOT / case_id
    with (folder / "Nodes.csv").open(encoding="utf-8-sig", newline="") as file:
        nodes = [row["node_id"] for row in csv.DictReader(file)]
    graph = FlowGraph(nodes)
    with (folder / "Edges.csv").open(encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            graph.add_edge(row["edge_id"], row["from_node_id"],
                           row["to_node_id"], int(row["capacity"]))
    return graph
