"""Edmonds–Karp = Ford–Fulkerson tìm đường tăng bằng BFS."""

from bfs import bfs
from graph import (
    augment,
    path_from_parent,
    path_names,
    path_arcs,
    ensure_zero_flow
)


def edmonds_karp(graph, source="SS", sink="TT", save_history=True):
    if source == sink or source not in graph.adj or sink not in graph.adj:
        raise ValueError("Nguồn/đích không hợp lệ")

    ensure_zero_flow(graph)

    max_flow = 0
    history = []

    while True:
        parent = bfs(graph, source, sink)

        if parent is None:
            break

        path = path_from_parent(graph, parent, source, sink)

        delta = min(graph.adj[u][i]["res"] for u, i in path)

        # Chỉ thu thập thông tin khi bật lịch sử.
        if save_history:
            names = path_names(graph, path, source)
            selected_arcs = path_arcs(graph, path)

        augment(graph, path, delta)
        max_flow += delta

        # Chỉ lưu lịch sử khi được yêu cầu.
        if save_history:
            history.append({
                "iteration": len(history) + 1,
                "path": names,
                "path_arcs": selected_arcs,
                "bottleneck": delta,
                "total_flow": max_flow,
                "residual_snapshot": graph.residual_arcs()
            })

    return max_flow, history
