"""Chạy SMART INTERSECTION: python main.py --all --history"""
import argparse
import csv
from pathlib import Path

from scenario import load_scenario, available_scenarios
from edmonds_karp import edmonds_karp
from ford_fulkerson import ford_fulkerson_dfs
from validator import verify_max_flow, check_movement_demands


def analyze(sid, show_history=False):
    original, movements, lanes, info = load_scenario(sid)
    graph_bfs = original.clone()
    graph_dfs = original.clone()

    max_flow, history = edmonds_karp(graph_bfs)
    valid = verify_max_flow(graph_bfs, max_flow)
    dfs_flow, dfs_history = ford_fulkerson_dfs(graph_dfs)
    verify_max_flow(graph_dfs, dfs_flow)
    if max_flow != dfs_flow:
        raise AssertionError("DFS và BFS khác giá trị Max Flow")

    movement_flows = check_movement_demands(graph_bfs, movements)
    demand = sum(item["demand"] for item in movement_flows)
    if sum(item["flow"] for item in movement_flows) != max_flow:
        raise AssertionError("Luồng 12 movement không bằng tổng Max Flow")

    print("\n%s – %s" % (sid, info["scenario_name"]))
    print("Demand=%s; MaxFlow=%s; MinCut=%s; Chưa phục vụ=%s" % (
        demand, max_flow, valid["cut_capacity"], demand - max_flow))
    print("BFS: %s lần tăng | DFS: %s lần tăng | Kiểm chứng: PASS" % (
        len(history), len(dfs_history)))
    print("S:", ", ".join(sorted(valid["S"])))
    print("T:", ", ".join(sorted(valid["T"])))
    print("Cut edges:", ", ".join(e["edge_id"] for e in valid["cut_edges"]))

    if show_history:
        for step in history:
            print("  Lần %02d: %s | delta=%s | F=%s" % (
                step["iteration"], " -> ".join(step["path"]),
                step["bottleneck"], step["total_flow"]))

    return {"scenario_id": sid, "demand": demand, "max_flow": max_flow,
            "min_cut": valid["cut_capacity"], "unserved": demand-max_flow,
            "bfs_iterations": len(history), "dfs_iterations": len(dfs_history),
            "history": history, "movement_flows": movement_flows,
            "cut_edges": valid["cut_edges"], "S": sorted(valid["S"]),
            "T": sorted(valid["T"]),
            "edge_flows": graph_bfs.original_flows(),
            "residual_final": graph_bfs.residual_arcs()}


def save_results(results, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    with (output / "summary.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "scenario_id", "demand", "max_flow", "min_cut", "unserved",
            "bfs_iterations", "dfs_iterations"])
        writer.writeheader()
        for r in results:
            writer.writerow({k: r[k] for k in writer.fieldnames})

    with (output / "movement_flows.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "scenario_id", "movement_id", "demand", "flow", "unserved"])
        writer.writeheader()
        for r in results:
            for movement in r["movement_flows"]:
                writer.writerow({"scenario_id": r["scenario_id"], **movement})

    with (output / "min_cut.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "scenario_id", "edge_id", "from", "to", "capacity"])
        writer.writeheader()
        for r in results:
            for edge in r["cut_edges"]:
                writer.writerow({"scenario_id": r["scenario_id"], **edge})

    with (output / "augmenting_paths.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "scenario_id", "iteration", "path", "bottleneck", "total_flow",
            "selected_residual_arcs"])
        writer.writeheader()
        for r in results:
            for step in r["history"]:
                writer.writerow({"scenario_id": r["scenario_id"],
                                 "iteration": step["iteration"],
                                 "path": " -> ".join(step["path"]),
                                 "bottleneck": step["bottleneck"],
                                 "total_flow": step["total_flow"],
                                 "selected_residual_arcs": "; ".join(
                                     f'{arc["edge_id"]}:{arc["arc_type"]}:'
                                     f'{arc["from"]}->{arc["to"]}@{arc["arc_index"]}'
                                     for arc in step["path_arcs"])})
    with (output / "edge_flows.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "scenario_id", "edge_id", "from", "to", "capacity", "flow"])
        writer.writeheader()
        for r in results:
            for edge in r["edge_flows"]:
                writer.writerow({"scenario_id": r["scenario_id"], **edge})

    # Từng ảnh chụp mạng dư SAU mỗi vòng tăng luồng (88 cung / vòng với 44 cạnh gốc).
    # Thứ tự iteration = 1, 2, ... để website phát lại quá trình Edmonds–Karp.
    with (output / "residual_steps.csv").open("w", encoding="utf-8-sig", newline="") as f:
        fields = ["scenario_id", "iteration", "total_flow", "edge_id",
                  "arc_type", "from", "to", "residual"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in results:
            for step in r["history"]:
                for arc in step["residual_snapshot"]:
                    writer.writerow({"scenario_id": r["scenario_id"],
                                     "iteration": step["iteration"],
                                     "total_flow": step["total_flow"], **arc})

    with (output / "residual_final.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "scenario_id", "edge_id", "arc_type", "from", "to", "residual"])
        writer.writeheader()
        for r in results:
            for arc in r["residual_final"]:
                writer.writerow({"scenario_id": r["scenario_id"], **arc})
    print("\nĐã xuất CSV kết quả vào:", output)


def main():
    parser = argparse.ArgumentParser(description="SMART INTERSECTION – Max Flow")
    parser.add_argument("--scenario", choices=sorted(available_scenarios()), default="SC02")
    parser.add_argument("--all", action="store_true", help="Chạy 5 kịch bản")
    parser.add_argument("--history", action="store_true", help="In từng đường tăng luồng")
    parser.add_argument("--output", default="outputs", help="Thư mục xuất CSV")
    args = parser.parse_args()

    ids = sorted(available_scenarios()) if args.all else [args.scenario]
    results = [analyze(sid, args.history) for sid in ids]
    save_results(results, args.output)


if __name__ == "__main__":
    main()
