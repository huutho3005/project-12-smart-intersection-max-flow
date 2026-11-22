"""Lát cắt tối thiểu tìm từ mạng dư SAU khi đã chạy Max Flow."""


def reachable_from_source(graph, source="SS"):
    visited = {source}
    queue = [source]
    head = 0

    while head < len(queue):
        u = queue[head]
        head += 1
        for arc in graph.adj[u]:
            v = arc["to"]
            if arc["res"] > 0 and v not in visited:
                visited.add(v)
                queue.append(v)
    return visited


def min_cut(graph, source="SS", sink="TT"):
    S = reachable_from_source(graph, source)
    if sink in S:
        raise ValueError("Còn đường tăng luồng: chưa thể xuất Minimum Cut")
    T = set(graph.nodes) - S

    cut_edges = []
    cut_capacity = 0
    for edge in graph.edges:
        if edge["u"] in S and edge["v"] in T:
            cut_edges.append({"edge_id": edge["id"], "from": edge["u"],
                              "to": edge["v"], "capacity": edge["capacity"]})
            cut_capacity += edge["capacity"]
    return S, T, cut_edges, cut_capacity
