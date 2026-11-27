"""Phân tích độ nhạy lưu lượng cực đại trên SC02."""

import csv
from pathlib import Path

from graph import FlowGraph
from scenario import load_scenario
from edmonds_karp import edmonds_karp
from ford_fulkerson import ford_fulkerson_dfs
from validator import verify_max_flow

ROOT = Path(__file__).resolve().parent


def build_variant(
    base,
    capacity_add=None,
    relax_demand=False,
    lane_percent=100
):
    """Tạo mạng mới, không sửa dữ liệu gốc."""

    capacity_add = capacity_add or {}
    graph = FlowGraph(base.nodes)

    # Tổng năng lực các hướng thoát.
    exit_capacity = sum(
        e["capacity"]
        for e in base.edges
        if e["u"].startswith("EXIT_") and e["v"] == "TT"
    )

    for edge in base.edges:
        u = edge["u"]
        v = edge["v"]
        capacity = edge["capacity"]

        # Nới giới hạn Demand đầu vào.
        if relax_demand:
            if u == "SS" or (
                u.startswith("APP_")
                and v.startswith("LG_")
            ):
                capacity = exit_capacity

        capacity += capacity_add.get(edge["id"], 0)

        # Làm tròn half-up khi thay đổi năng lực nhóm làn.
        if u.startswith("LG_") and v.startswith("MOV_"):
            capacity = (capacity * lane_percent + 50) // 100

        graph.add_edge(edge["id"], u, v, capacity)

    return graph


def run_case(
    base,
    case_id,
    description,
    capacity_add=None,
    relax_demand=False,
    lane_percent=100
):
    """Chạy BFS, DFS và kiểm chứng Min-Cut."""

    graph = build_variant(
        base,
        capacity_add,
        relax_demand,
        lane_percent
    )

    g_bfs = graph.clone()
    g_dfs = graph.clone()

    flow_bfs, _ = edmonds_karp(
        g_bfs, save_history=False
    )

    flow_dfs, _ = ford_fulkerson_dfs(
        g_dfs, save_history=False
    )

    result_bfs = verify_max_flow(g_bfs, flow_bfs)
    result_dfs = verify_max_flow(g_dfs, flow_dfs)

    cut = result_bfs["cut_capacity"]

    if not (
        flow_bfs == flow_dfs
        == cut == result_dfs["cut_capacity"]
    ):
        raise AssertionError(
            "Kết quả không khớp tại " + case_id
        )

    return {
        "case_id": case_id,
        "description": description,
        "max_flow_bfs": flow_bfs,
        "max_flow_dfs": flow_dfs,
        "min_cut": cut,
        "cut_edges": ";".join(
            e["edge_id"]
            for e in result_bfs["cut_edges"]
        ),
        "S": ";".join(sorted(result_bfs["S"])),
        "T": ";".join(sorted(result_bfs["T"]))
    }


def main():
    base, _, _, _ = load_scenario("SC02")

    cases = [
        ("SC02_BASE", "SC02 gốc", {}, False, 100),
        ("RELAX_DEMAND", "Nới giới hạn Demand", {}, True, 100),
        ("E021_PLUS_100", "Tăng E021 thêm 100", {"E021": 100}, False, 100),
        ("E027_PLUS_100", "Tăng E027 thêm 100", {"E027": 100}, False, 100),
        ("BOTH_PLUS_100", "Tăng E021 và E027 thêm 100",
         {"E021": 100, "E027": 100}, False, 100),
        ("LANE_MINUS_10", "Giảm Capacity nhóm làn 10%", {}, False, 90),
        ("LANE_PLUS_10", "Tăng Capacity nhóm làn 10%", {}, False, 110),
    ]

    results = [run_case(base, *case) for case in cases]

    baseline = results[0]["max_flow_bfs"]

    for row in results:
        row["delta_vs_SC02"] = (
            row["max_flow_bfs"] - baseline
        )

    output = ROOT / "outputs" / "sensitivity_analysis.csv"
    output.parent.mkdir(parents=True, exist_ok=True)

    fields = [
        "case_id",
        "description",
        "max_flow_bfs",
        "max_flow_dfs",
        "min_cut",
        "delta_vs_SC02",
        "cut_edges",
        "S",
        "T"
    ]

    with output.open(
        "w", encoding="utf-8-sig", newline=""
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    print("Phân tích độ nhạy - SC02")

    for row in results:
        print(
            row["case_id"],
            "| BFS =", row["max_flow_bfs"],
            "| DFS =", row["max_flow_dfs"],
            "| MinCut =", row["min_cut"],
            "| Delta =", row["delta_vs_SC02"],
            "| PASS"
        )

    print("\nĐã xuất:", output)


if __name__ == "__main__":
    main()
