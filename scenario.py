"""Đọc CSV đã chốt. Không tự sinh hoặc sửa Capacity trong code."""
import csv
from pathlib import Path
from graph import FlowGraph
from validator import validate_structure, validate_scenario_metadata

BASE = Path(__file__).resolve().parent / "data"


def read_csv(filename):
    with Path(filename).open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def available_scenarios():
    return {s["scenario_id"]: s for s in read_csv(BASE / "Scenarios.csv")}


def load_scenario(scenario_id):
    catalog = available_scenarios()
    if scenario_id not in catalog:
        raise ValueError("Không có kịch bản: " + scenario_id)

    nodes = read_csv(BASE / "Nodes.csv")
    folder = BASE / "scenarios" / scenario_id
    edges = read_csv(folder / "Edges.csv")
    lane_groups = read_csv(folder / "Lane_Groups.csv")
    movements = read_csv(folder / "Movements.csv")

    graph = FlowGraph([row["node_id"] for row in nodes])
    for row in edges:
        graph.add_edge(row["edge_id"], row["from_node_id"],
                       row["to_node_id"], int(row["capacity"]))
    validate_structure(graph, expected_nodes=34, expected_edges=44)

    if len(movements) != 12 or len(lane_groups) != 12:
        raise ValueError("Sai số lượng movement hoặc lane group")

    # Đối chiếu Demand tổng từ movement với Scenarios.csv.
    demand_total = sum(int(m["demand_scenario"]) for m in movements)
    expected = int(catalog[scenario_id]["demand_scenario_total"])
    if demand_total != expected:
        raise ValueError("Demand của kịch bản không khớp Scenarios.csv")

    # Bảng movement theo kịch bản phải phản ánh nguồn của cạnh LG->MOV.
    for m in movements:
        mid = m["movement_id"]
        sources = [e["u"] for e in graph.edges if e["v"] == mid]
        if sources != [m["lane_group_id"]]:
            raise ValueError("Mapping lane group/movement sai tại " + mid)
    validate_scenario_metadata(graph, movements, lane_groups, scenario_id)
    return graph, movements, lane_groups, catalog[scenario_id]
