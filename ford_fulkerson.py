"""Ford–Fulkerson với DFS tìm một đường tăng luồng bất kỳ."""
from graph import (
    augment,
    path_names,
    ensure_zero_flow,
    path_from_parent
)


def dfs_path(graph, source, sink):
    """DFS dùng Stack và Parent, không sử dụng đệ quy."""

    if source == sink:
        return []

    parent = {source: None}
    stack = [(source, 0)]

    while stack:
        u, i = stack[-1]

        # Đã duyệt hết cung kề của u.
        if i == len(graph.adj[u]):
            stack.pop()
            continue

        # Lưu vị trí cung tiếp theo cần duyệt.
        stack[-1] = (u, i + 1)

        arc = graph.adj[u][i]
        v = arc["to"]

        # Bỏ qua cung hết dung lượng hoặc đỉnh đã thăm.
        if arc["res"] <= 0 or v in parent:
            continue

        parent[v] = (u, i)

        # Tìm thấy đích, truy vết đường đi.
        if v == sink:
            return path_from_parent(
                graph, parent, source, sink
            )

        stack.append((v, 0))

    return None


    return visit(source)


def ford_fulkerson_dfs(graph, source="SS", sink="TT", save_history=True):
    if source == sink or source not in graph.adj or sink not in graph.adj:
        raise ValueError("Nguồn/đích không hợp lệ")

    ensure_zero_flow(graph)

    total = 0
    history = []

    while True:
        path = dfs_path(graph, source, sink)

        if path is None:
            break

        delta = min(graph.adj[u][i]["res"] for u, i in path)

        # Chỉ lấy tên đường đi khi bật lịch sử.
        if save_history:
            names = path_names(graph, path, source)

        augment(graph, path, delta)
        total += delta

        # Chỉ lưu lịch sử khi được yêu cầu.
        if save_history:
            history.append({
                "iteration": len(history) + 1,
                "path": names,
                "bottleneck": delta,
                "total_flow": total
            })

    return total, history
