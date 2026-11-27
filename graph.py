"""Cấu trúc đồ thị và mạng dư; chỉ dùng thư viện chuẩn Python."""


class FlowGraph:
    def __init__(self, nodes):
        self.nodes = list(nodes)
        if len(self.nodes) != len(set(self.nodes)):
            raise ValueError("Trùng tên đỉnh")
        self.adj = {u: [] for u in self.nodes}
        self.edges = []  # Các cạnh GỐC, không gồm cạnh ngược mạng dư
        self.edge_ids = set()  # Tra cứu mã cạnh đã có: trung bình O(1)

    def add_edge(self, edge_id, u, v, capacity):
        if u not in self.adj or v not in self.adj:
            raise ValueError("Cạnh %s có đỉnh không tồn tại" % edge_id)
        if u == v:
            raise ValueError("Không dùng khuyên (self-loop): %s" % edge_id)
        if type(capacity) is not int or capacity < 0:
            raise ValueError("Capacity không hợp lệ tại %s" % edge_id)
        if edge_id in self.edge_ids:
            raise ValueError("Trùng mã cạnh: %s" % edge_id)

        # Chỉ số để hai cung dư biết cung đảo tương ứng.
        i = len(self.adj[u])
        j = len(self.adj[v])
        # Định danh từng CUNG DƯ: không suy luận forward/reverse từ tên đỉnh.
        # Điều này quan trọng khi tồn tại đồng thời cạnh gốc u->v và v->u.
        self.adj[u].append({"to": v, "res": capacity, "rev": j,
                            "edge_id": edge_id, "arc_type": "forward"})
        self.adj[v].append({"to": u, "res": 0, "rev": i,
                            "edge_id": edge_id, "arc_type": "reverse"})
        self.edges.append({"id": edge_id, "u": u, "v": v,
                           "capacity": capacity, "index": i})
        self.edge_ids.add(edge_id)

    def original_flows(self):
        """Luồng từng cạnh gốc = Capacity - dung lượng dư thuận."""
        result = []
        for edge in self.edges:
            remaining = self.adj[edge["u"]][edge["index"]]["res"]
            result.append({"edge_id": edge["id"], "from": edge["u"],
                           "to": edge["v"], "capacity": edge["capacity"],
                           "flow": edge["capacity"] - remaining})
        return result

    def residual_arcs(self):
        """Xuất cả cung dư thuận/ngược theo từng cạnh gốc (kể cả Residual=0)."""
        result = []
        for edge in self.edges:
            u = edge["u"]
            fwd = self.adj[u][edge["index"]]
            v = edge["v"]
            backward = self.adj[v][fwd["rev"]]
            result.append({"edge_id": edge["id"], "arc_type": "forward",
                           "from": u, "to": v, "residual": fwd["res"]})
            result.append({"edge_id": edge["id"], "arc_type": "reverse",
                           "from": v, "to": u, "residual": backward["res"]})
        return result

    def clone(self):
        """Tạo đồ thị mới để DFS và BFS không dùng chung mạng dư bị thay đổi."""
        copy = FlowGraph(self.nodes)
        for edge in self.edges:
            copy.add_edge(edge["id"], edge["u"], edge["v"], edge["capacity"])
        return copy


def augment(graph, path, delta):
    """Cập nhật mạng dư trên đường tăng: R(u,v)-=delta, R(v,u)+=delta."""
    if delta <= 0:
        raise ValueError("Bottleneck phải dương")
    for u, i in path:
        arc = graph.adj[u][i]
        if arc["res"] < delta:
            raise ValueError("Bottleneck vượt quá dung lượng dư")
    for u, i in path:
        arc = graph.adj[u][i]
        arc["res"] -= delta
        graph.adj[arc["to"]][arc["rev"]]["res"] += delta


def path_from_parent(graph, parent, source, sink):
    """Trả về danh sách (đỉnh đầu, chỉ số cung dư) theo thứ tự nguồn-đích."""
    if sink not in parent:
        return []
    result = []
    v = sink
    while v != source:
        u, i = parent[v]
        result.append((u, i))
        v = u
    result.reverse()
    return result


def path_arcs(graph, path):
    """Trả về metadata chính xác của các CUNG DƯ BFS đã chọn.

    Mỗi phần tử path là (u, index) do parent[v] lưu khi BFS thực thi.
    Vì vậy đây là danh tính cung thực tế, ngay cả với cạnh song song/ngược chiều.
    """
    result = []
    for u, i in path:
        arc = graph.adj[u][i]
        result.append({"from": u, "to": arc["to"],
                       "edge_id": arc["edge_id"],
                       "arc_type": arc["arc_type"],
                       "arc_index": i, "reverse_index": arc["rev"]})
    return result


def path_names(graph, path, source):
    names = [source]
    for u, i in path:
        names.append(graph.adj[u][i]["to"])
    return names



def ensure_zero_flow(graph):
    """Kiểm tra đồ thị chưa có luồng trước khi chạy thuật toán."""

    for edge in graph.original_flows():
        if edge["flow"] != 0:
            raise ValueError(
                "Đồ thị đã có luồng. Hãy sử dụng graph.clone()."
            )

    return True
