"""Ford–Fulkerson với DFS tìm một đường tăng luồng bất kỳ."""
from graph import augment, path_names


def dfs_path(graph, source, sink):
    """DFS trả về đường đi gồm các cung dư (u, index)."""
    visited = set()

    def visit(u):
        if u == sink:
            return []
        visited.add(u)
        for i, arc in enumerate(graph.adj[u]):
            v = arc["to"]
            if arc["res"] > 0 and v not in visited:
                rest = visit(v)
                if rest is not None:
                    return [(u, i)] + rest
        return None

    return visit(source)


def ford_fulkerson_dfs(graph, source="SS", sink="TT"):
    if source == sink or source not in graph.adj or sink not in graph.adj:
        raise ValueError("Nguồn/đích không hợp lệ")

    total = 0
    history = []
    while True:
        path = dfs_path(graph, source, sink)
        if path is None:
            break
        delta = min(graph.adj[u][i]["res"] for u, i in path)
        names = path_names(graph, path, source)
        augment(graph, path, delta)
        total += delta
        history.append({"iteration": len(history) + 1,
                        "path": names, "bottleneck": delta,
                        "total_flow": total})
    return total, history
