"""Kiểm tra cấu trúc, Capacity Constraint, Flow Conservation, Max-Flow Min-Cut."""
from bfs import bfs
from min_cut import min_cut


def validate_structure(graph, expected_nodes=None, expected_edges=None):
    if expected_nodes is not None and len(graph.nodes) != expected_nodes:
        raise ValueError("Sai số đỉnh")
    if expected_edges is not None and len(graph.edges) != expected_edges:
        raise ValueError("Sai số cạnh")
    if len(graph.nodes) != len(set(graph.nodes)):
        raise ValueError("Đỉnh trùng")
    if len(graph.edges) != len({e["id"] for e in graph.edges}):
        raise ValueError("Mã cạnh trùng")
    for edge in graph.edges:
        if edge["capacity"] < 0:
            raise ValueError("Capacity âm tại " + edge["id"])
        if edge["u"] not in graph.adj or edge["v"] not in graph.adj:
            raise ValueError("Đỉnh không tồn tại ở " + edge["id"])
    return True


def check_capacity_constraint(graph):
    """Với mọi cạnh gốc: 0 <= f(e) <= C(e)."""
    for e in graph.original_flows():
        if not (0 <= e["flow"] <= e["capacity"]):
            raise AssertionError("Capacity Constraint sai tại " + e["edge_id"])
    return True


def check_flow_conservation(graph, source="SS", sink="TT"):
    """Tổng luồng vào == tổng luồng ra tại mọi đỉnh trung gian."""
    balance = {u: 0 for u in graph.nodes}
    for e in graph.original_flows():
        balance[e["from"]] -= e["flow"]
        balance[e["to"]] += e["flow"]
    for u in graph.nodes:
        if u not in (source, sink) and balance[u] != 0:
            raise AssertionError("Không bảo toàn luồng tại " + u)
    if balance[source] != -balance[sink]:
        raise AssertionError("Luồng ròng nguồn và đích không cân bằng")
    return balance[sink]


def verify_max_flow(graph, max_flow, source="SS", sink="TT"):
    """Kiểm tra độc lập: luồng hợp lệ + không còn đường tăng + MinCut bằng MaxFlow."""
    check_capacity_constraint(graph)
    value_at_sink = check_flow_conservation(graph, source, sink)
    if value_at_sink != max_flow:
        raise AssertionError("Giá trị luồng không khớp luồng vào đích")
    if bfs(graph, source, sink) is not None:
        raise AssertionError("Vẫn còn đường tăng luồng")
    S, T, cut_edges, cut_capacity = min_cut(graph, source, sink)
    if cut_capacity != max_flow:
        raise AssertionError("Max-Flow không bằng Min-Cut")
    return {"valid": True, "S": S, "T": T,
            "cut_edges": cut_edges, "cut_capacity": cut_capacity}


def check_movement_demands(graph, movements):
    """Luồng trên LG->MOV không vượt Demand từng movement."""
    flow_to_movement = {m["movement_id"]: 0 for m in movements}
    for e in graph.original_flows():
        if e["to"] in flow_to_movement and e["from"].startswith("LG_"):
            flow_to_movement[e["to"]] += e["flow"]
    result = []
    for m in movements:
        mid = m["movement_id"]
        demand = int(m["demand_scenario"])
        flow = flow_to_movement[mid]
        if not 0 <= flow <= demand:
            raise AssertionError("Luồng vượt Demand của " + mid)
        result.append({"movement_id": mid, "demand": demand,
                       "flow": flow, "unserved": demand - flow})
    return result


def validate_scenario_metadata(graph, movements, lane_groups, scenario_id):
    """Kiểm tra dữ liệu SC01–SC05 khớp cả 3 bảng Edges/Lane_Groups/Movements.

    Không sửa số liệu hay tự sinh Capacity; chỉ phát hiện sai lệch CSV.
    """
    lane_by_id = {row["lane_group_id"]: row for row in lane_groups}
    mov_by_id = {row["movement_id"]: row for row in movements}
    if len(lane_by_id) != 12 or len(mov_by_id) != 12:
        raise ValueError("Trùng hoặc thiếu mã Lane Group / Movement")

    for row in lane_groups + movements:
        if row["scenario_id"] != scenario_id:
            raise ValueError("Metadata sai scenario_id tại " +
                             row.get("lane_group_id", row.get("movement_id", "")))

    # Với mỗi movement, kiểm tra đường đi và hướng ra đúng với bảng mô tả.
    assigned = {lg: set() for lg in lane_by_id}
    demand_by_approach = {direction: 0 for direction in "NSEW"}
    for mid, movement in mov_by_id.items():
        lg = movement["lane_group_id"]
        if lg not in lane_by_id:
            raise ValueError("Lane Group không tồn tại cho " + mid)
        assigned[lg].add(mid)
        demand_by_approach[movement["origin_direction"]] += int(
            movement["demand_scenario"])
        arrivals = [e for e in graph.edges if e["v"] == mid and e["u"].startswith("LG_")]
        if len(arrivals) != 1 or arrivals[0]["u"] != lg:
            raise ValueError("Sai kết nối Lane Group -> Movement: " + mid)
        exits = [e for e in graph.edges if e["u"] == mid and e["v"].startswith("EXIT_")]
        if len(exits) != 1 or exits[0]["v"] != "EXIT_" + movement["exit_direction"]:
            raise ValueError("Sai hướng thoát của " + mid)

    # SS -> APP cần có dung lượng bằng tổng Demand từng hướng trong mô hình này.
    for direction, demand in demand_by_approach.items():
        approach = "APP_" + direction
        links = [e for e in graph.edges if e["u"] == "SS" and e["v"] == approach]
        if len(links) != 1 or links[0]["capacity"] != demand:
            raise ValueError("Sai tổng Demand cạnh SS -> " + approach)

    for lg, lane in lane_by_id.items():
        mapped = set(filter(None, lane["assigned_movements"].split(";")))
        if mapped != assigned[lg]:
            raise ValueError("Không đồng bộ assigned_movements tại " + lg)
        active = lane["is_active"] == "1"
        lane_count = int(lane["lane_count"])
        capacity = int(lane["capacity_effective"])
        incoming = [e for e in graph.edges if e["v"] == lg and e["u"].startswith("APP_")]
        outgoing = [e for e in graph.edges if e["u"] == lg and e["v"].startswith("MOV_")]
        if len(incoming) != 1 or len(outgoing) != len(mapped):
            raise ValueError("Số kết nối không đúng tại " + lg)
        if not active:
            if lane_count != 0 or capacity != 0 or mapped or incoming[0]["capacity"] != 0:
                raise ValueError("Nhóm làn ngừng hoạt động chưa đồng bộ: " + lg)
        else:
            if lane_count <= 0 or capacity <= 0 or not mapped:
                raise ValueError("Nhóm làn hoạt động thiếu Capacity/làn: " + lg)
            if len(mapped) == 1:
                # Làn riêng: giới hạn vật lý ở LG -> MOV.
                if outgoing[0]["capacity"] != capacity:
                    raise ValueError("Capacity nhóm làn không khớp: " + lg)
                only_mid = next(iter(mapped))
                if incoming[0]["capacity"] != int(mov_by_id[only_mid]["demand_scenario"]):
                    raise ValueError("Demand đầu vào nhóm làn không khớp: " + lg)
            else:
                # Làn dùng chung: giới hạn chung ở APP -> LG.
                if incoming[0]["capacity"] != capacity:
                    raise ValueError("Capacity dùng chung không khớp: " + lg)
                for edge in outgoing:
                    if edge["capacity"] != int(mov_by_id[edge["v"]]["demand_scenario"]):
                        raise ValueError("Demand riêng movement không khớp: " + edge["v"])
    return True
