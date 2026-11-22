"""Cầu nối dữ liệu giữa website và 8 module thuật toán đã kiểm chứng.

KHÔNG cài đặt lại BFS/DFS/Edmonds-Karp/Min-Cut và không gán cứng kết quả.
"""
from scenario import load_scenario, available_scenarios
from edmonds_karp import edmonds_karp
from ford_fulkerson import ford_fulkerson_dfs
from validator import verify_max_flow, check_movement_demands


def scenario_catalog():
    return available_scenarios()


def run_scenario(scenario_id):
    """Tự đọc CSV và tự tính lại từ đầu; không làm biến đổi data trên đĩa."""
    original, movements, lanes, info = load_scenario(scenario_id)
    graph_bfs = original.clone()
    graph_dfs = original.clone()  # DFS và BFS không chia sẻ mạng dư

    max_flow, history = edmonds_karp(graph_bfs)
    validated = verify_max_flow(graph_bfs, max_flow)
    dfs_flow, dfs_history = ford_fulkerson_dfs(graph_dfs)
    verify_max_flow(graph_dfs, dfs_flow)
    if max_flow != dfs_flow:
        raise AssertionError("DFS khác BFS: " + scenario_id)

    movement_flows = check_movement_demands(graph_bfs, movements)
    demand = sum(int(row["demand_scenario"]) for row in movements)
    if sum(row["flow"] for row in movement_flows) != max_flow:
        raise AssertionError("Tổng luồng movement không bằng Maximum Flow")

    return {
        "scenario_id": scenario_id, "scenario": info,
        "nodes": list(original.nodes), "edges": list(original.edges),
        "movements": movements, "lane_groups": lanes,
        "demand": demand, "max_flow": max_flow, "dfs_flow": dfs_flow,
        "unserved": demand - max_flow,
        "satisfaction_pct": 100 * max_flow / demand if demand else 100.0,
        "history": history, "dfs_history": dfs_history,
        "min_cut": validated["cut_capacity"],
        "S": sorted(validated["S"]), "T": sorted(validated["T"]),
        "cut_edges": validated["cut_edges"],
        "edge_flows": graph_bfs.original_flows(),
        "movement_flows": movement_flows,
        "residual_final": graph_bfs.residual_arcs(),
    }


def run_all():
    """Chạy 5 kịch bản thật trên cùng bộ thuật toán."""
    return [run_scenario(sid) for sid in sorted(scenario_catalog())]


def cut_category(edge_id, scenario_id=None, edge=None, lane_groups=None):
    """Phân loại lát cắt bằng metadata, không suy luận riêng từ dải ID.

    Cạnh APP -> LG với capacity=0 do LG ngừng hoạt động không phải
    giới hạn Demand, ngay cả khi ID thuộc E005-E016.
    """
    if edge is not None and lane_groups is not None and scenario_id is not None:
        target = edge["to"]
        if edge["capacity"] == 0 and target.startswith("LG_"):
            for lane in lane_groups:
                if (lane["lane_group_id"] == target and
                        str(lane["is_active"]).strip().lower() in {"0", "false", "no"}):
                    return f"Nhóm làn không hoạt động ({scenario_id})"

    n = int(edge_id[1:])
    if 5 <= n <= 16:
        return "Giới hạn Demand"
    if 17 <= n <= 28:
        return "Năng lực nhóm làn"
    if 41 <= n <= 44:
        return "Khả năng tiếp nhận lối ra"
    return "Cạnh khác"


def cut_meaning(edge, category=None):
    if category is None:
        category = cut_category(edge["edge_id"])
    if category.startswith("Nhóm làn không hoạt động"):
        return ("Nhóm làn " + edge["to"] +
                " ngừng hoạt động theo kịch bản; "
                "đây không phải điểm nghẽn hạ tầng vật lý")
    if edge["capacity"] == 0:
        return "Dung lượng bằng 0; cần kiểm tra quy tắc và metadata cạnh"
    if category == "Giới hạn Demand":
        return "Giới hạn nhu cầu của " + edge["to"].replace("LG_", "")
    if category == "Năng lực nhóm làn":
        return "Năng lực nhóm làn " + edge["from"].replace("LG_", "")
    if category == "Khả năng tiếp nhận lối ra":
        return "Hướng thoát " + edge["from"].replace("EXIT_", "")
    return "Kiểm tra lại kết nối"


def cut_display_rows(result):
    """Chuẩn bị bảng Minimum Cut có ngữ cảnh scenario & metadata nhóm làn."""
    rows = []
    for edge in result["cut_edges"]:
        kind = cut_category(edge["edge_id"],
                            scenario_id=result["scenario_id"],
                            edge=edge, lane_groups=result["lane_groups"])
        rows.append({
            "Edge ID": edge["edge_id"],
            "Từ": edge["from"], "Đến": edge["to"],
            "Capacity": edge["capacity"],
            "Loại giới hạn": kind,
            "Ý nghĩa giao thông": cut_meaning(edge, category=kind),
        })
    return rows


def cut_partition_table(result):
    """Hai cột đỉnh S/T; một đỉnh mỗi dòng, danh sách dài không bị cắt ngang."""
    left, right = result["S"], result["T"]
    count = max(len(left), len(right))
    return {
        f"Tập S ({len(left)} đỉnh)": left + [""] * (count - len(left)),
        f"Tập T ({len(right)} đỉnh)": right + [""] * (count - len(right)),
    }
