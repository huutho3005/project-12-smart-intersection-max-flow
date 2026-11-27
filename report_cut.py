"""Báo cáo kiểm chứng DFS/BFS/Min-Cut từ đúng dữ liệu SC01–SC05.
Chạy: python report_cut.py
Dùng thư viện chuẩn, không cần networkx.
"""
import csv
from pathlib import Path
from scenario import load_scenario
from edmonds_karp import edmonds_karp
from ford_fulkerson import ford_fulkerson_dfs
from validator import verify_max_flow

OUTPUT = Path(__file__).resolve().parent / "outputs"


def edge_kind(edge_id):
    n = int(edge_id[1:])
    if 5 <= n <= 16:
        return "DEMAND", "Giới hạn nhu cầu chuyển động tại đầu vào"
    if 17 <= n <= 28:
        return "LANE", "Giới hạn năng lực nhóm làn/chuyển động"
    if 41 <= n <= 44:
        return "EXIT", "Giới hạn tiếp nhận tại hướng thoát"
    return "OTHER", "Kiểm tra ý nghĩa kết nối"


def explain_cut(edge):
    kind, base = edge_kind(edge["edge_id"])
    if edge["capacity"] == 0:
        return "Cạnh vô hiệu hóa chủ đích (không diễn giải là điểm nghẽn vật lý)"
    if kind == "EXIT":
        return "Lối ra " + edge["from"].replace("EXIT_", "") + " đạt giới hạn tiếp nhận"
    if kind == "LANE":
        return "Năng lực nhóm làn " + edge["from"].replace("LG_", "") + " giới hạn luồng"
    if kind == "DEMAND":
        return "Nhu cầu nhánh " + edge["to"].replace("LG_", "") + " giới hạn luồng; không suy ra ùn tắc vật lý"
    return base


def write_csv(path, fields, records):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(records)


def run():
    OUTPUT.mkdir(exist_ok=True, parents=True)
    summary = []
    details = []
    for sid in ["SC01", "SC02", "SC03", "SC04", "SC05"]:
        input_g, mov, lanes, info = load_scenario(sid)
        bfs_g = input_g.clone()  # KHÔNG dùng chung mạng dư đã thay đổi
        dfs_g = input_g.clone()

        f_bfs, history_bfs = edmonds_karp(bfs_g)
        f_dfs, history_dfs = ford_fulkerson_dfs(dfs_g)
        v_bfs = verify_max_flow(bfs_g, f_bfs)
        v_dfs = verify_max_flow(dfs_g, f_dfs)
        assert f_bfs == f_dfs == v_bfs["cut_capacity"] == v_dfs["cut_capacity"]
        demand = sum(int(m["demand_scenario"]) for m in mov)
        cut = v_bfs["cut_edges"]
        part = {"DEMAND": 0, "LANE": 0, "EXIT": 0, "OTHER": 0}
        for e in cut:
            kind, _ = edge_kind(e["edge_id"])
            part[kind] += e["capacity"]
            # Mỗi cạnh S -> T phải bị bão hòa ở nghiệm max-flow.
            match = [x for x in bfs_g.original_flows() if x["edge_id"] == e["edge_id"]]
            assert len(match) == 1 and match[0]["flow"] == e["capacity"]
            details.append({
                "scenario_id": sid, "edge_id": e["edge_id"],
                "from_node": e["from"], "to_node": e["to"],
                "edge_category": kind, "capacity": e["capacity"],
                "flow": match[0]["flow"], "explanation": explain_cut(e),
            })

        summary.append({
            "scenario_id": sid,
            "scenario_name": info["scenario_name"],
            "demand": demand,
            "max_flow_bfs": f_bfs,
            "max_flow_dfs": f_dfs,
            "min_cut_bfs": v_bfs["cut_capacity"],
            "min_cut_dfs": v_dfs["cut_capacity"],
            "bfs_augmentations": len(history_bfs),
            "dfs_augmentations": len(history_dfs),
            "cut_edge_ids": "; ".join(e["edge_id"] for e in cut),
            "cut_demand_capacity": part["DEMAND"],
            "cut_lane_capacity": part["LANE"],
            "cut_exit_capacity": part["EXIT"],
            "cut_s_size": len(v_bfs["S"]),
            "cut_t_size": len(v_bfs["T"]),
            "test_result": "PASS"
        })

    write_csv(OUTPUT / "BaoCao_DFS_BFS_MinCut_5KB.csv", list(summary[0]), summary)
    write_csv(OUTPUT / "ChiTiet_Canh_MinCut_5KB.csv", list(details[0]), details)

    print("Đã tạo các báo cáo tại", OUTPUT)
    for row in summary:
        print(row["scenario_id"], "BFS", row["max_flow_bfs"], "DFS", row["max_flow_dfs"], "MinCut", row["min_cut_bfs"], "lần tăng", row["bfs_augmentations"], row["dfs_augmentations"])


if __name__ == "__main__":
    run()
