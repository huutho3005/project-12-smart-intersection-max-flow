"""BFS tìm đường tăng luồng ngắn nhất theo SỐ CẠNH trong mạng dư."""


def bfs(graph, source, sink):
    # parent[v] = (u, i): đã đến v từ cung dư thứ i của u.
    # Đánh dấu bằng parent ngay khi phát hiện để tránh thăm trùng.
    parent = {source: None}
    queue = [source]
    head = 0

    while head < len(queue):
        u = queue[head]
        head += 1

        for i, arc in enumerate(graph.adj[u]):
            v = arc["to"]
            if arc["res"] > 0 and v not in parent:
                parent[v] = (u, i)
                if v == sink:
                    return parent
                queue.append(v)

    return None
