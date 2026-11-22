"""Edmonds–Karp = Ford–Fulkerson tìm đường tăng bằng BFS."""
from bfs import bfs
from graph import augment, path_from_parent, path_names, path_arcs


def edmonds_karp(graph, source="SS", sink="TT"):
    if source == sink or source not in graph.adj or sink not in graph.adj:
        raise ValueError("Nguồn/đích không hợp lệ")

    max_flow = 0
    history = []

    while True:
        parent = bfs(graph, source, sink)
        if parent is None:
            break

        path = path_from_parent(graph, parent, source, sink)
        delta = min(graph.adj[u][i]["res"] for u, i in path)
        names = path_names(graph, path, source)
        selected_arcs = path_arcs(graph, path)  # Chụp chính xác cung dư (u,index)
        augment(graph, path, delta)

        max_flow += delta
        # Chụp BẢN SAO toàn bộ 2 cung dư của mỗi cạnh gốc SAU mỗi lần tăng.
        # Không lưu tham chiếu đến graph.adj vì trạng thái sẽ tiếp tục thay đổi.
        history.append({"iteration": len(history) + 1,
                        "path": names, "path_arcs": selected_arcs,
                        "bottleneck": delta,
                        "total_flow": max_flow,
                        "residual_snapshot": graph.residual_arcs()})

    return max_flow, history
