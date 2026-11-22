# Ôn vấn đáp – code tay trước, giải thích sau

## 1. BFS trên mạng dư

```python
def bfs(graph, s, t):
    parent = {s: None}
    q = [s]
    head = 0
    while head < len(q):
        u = q[head]
        head += 1
        for i, edge in enumerate(graph.adj[u]):
            v = edge["to"]
            if v not in parent and edge["res"] > 0:
                parent[v] = (u, i)
                if v == t:
                    return parent
                q.append(v)
    return None
```

**Vì sao `parent[v] = (u,i)`?** Vì phải xác định đúng **cung dư** nào đã đi qua, nhất là khi có nhiều cạnh từ u đến v.

## 2. Edmonds–Karp (dùng các hàm BFS, truy vết và cập nhật của graph.py)

```python
def edmonds_karp(g, s, t):
    total = 0
    while True:
        parent = bfs(g, s, t)
        if parent is None:
            break
        path = path_from_parent(g, parent, s, t)
        delta = min(g.adj[u][i]["res"] for u, i in path)
        augment(g, path, delta)
        total += delta
    return total
```

**Giải thích:** Lặp BFS → đường tăng → bottleneck → cập nhật mạng dư → cộng luồng. Sau khi không còn đường SS–TT có dung lượng dư dương, đã đạt Max-Flow.

## 2A. Viết tay đầy đủ `path_from_parent()` (truy vết cung dư)

**Ý tưởng:** BFS lưu `parent[v] = (u, i)`, nghĩa là đã đi từ `u` đến `v` qua
**cung dư thứ `i` trong `g.adj[u]`**. Truy vết từ đích về nguồn, sau đó đảo
ngược danh sách để được đường tăng theo chiều nguồn → đích.

```python
def path_from_parent(g, parent, s, t):
    if t not in parent:
        return []

    path = []
    v = t
    while v != s:
        u, i = parent[v]       # i: chỉ số cung dư BFS đã chọn
        path.append((u, i))
        v = u
    path.reverse()
    return path
```

**Tự giải thích:** Vì sao phải giữ `(u, i)` thay vì chỉ lưu tên đỉnh `u`?
Vì có thể có **nhiều cung cùng đi từ u đến v** (cạnh song song, hoặc hai
cạnh gốc ngược chiều), nhưng chỉ một cung cụ thể được BFS chọn.

## 2B. Viết tay đầy đủ `augment()` (cập nhật mạng dư)

**Ý tưởng:** Với từng cung dư nằm trên đường tăng, giảm phần dư ở cung đang
được đi qua và tăng phần dư ở **đúng cung đảo liên kết bởi `rev`**.

```python
def augment(g, path, delta):
    if delta <= 0:
        raise ValueError("Bottleneck phai duong")
    for u, i in path:
        arc = g.adj[u][i]
        if arc["res"] < delta:
            raise ValueError("Vuot dung luong du")

    for u, i in path:
        arc = g.adj[u][i]
        arc["res"] -= delta
        g.adj[arc["to"]][arc["rev"]]["res"] += delta
```

**Tự giải thích:** Nếu `arc` là cung ngược của cạnh gốc thì cập nhật trên
có tác dụng **hủy bớt luồng cũ**, không phải cho phương tiện đi ngược chiều.
`rev` chỉ thẳng vào cung dư đối ứng nên vẫn đúng khi hai cạnh gốc cùng
có hai chiều hoặc có cạnh song song.

**Tự luyện:** Trên đồ thị mục 6.4, sau lượt `SS→A→C→TT`, cung dư
`C→A` của cạnh `A→C` có dư 1. Lượt `SS→B→C→A→D→TT` dùng cung này
và đưa Flow(A→C) từ 1 trở về 0. Hãy tự cập nhật hai cung dư trước khi
xem lại code.

## 3. Minimum Cut

```python
def min_cut(g, s):
    S = {s}
    q = [s]
    for u in q:
        for e in g.adj[u]:
            if e["res"] > 0 and e["to"] not in S:
                S.add(e["to"])
                q.append(e["to"])
    T = set(g.nodes) - S
    cut = [e for e in g.edges if e["u"] in S and e["v"] in T]
    capacity = sum(e["capacity"] for e in cut)
    return S, T, capacity
```

**Quan trọng:** dùng **mạng dư** để tìm S, T nhưng cộng **Capacity cạnh gốc** cho lát cắt.

## 4. Đồ thị tính tay 6 đỉnh / 7 cạnh

| Cạnh gốc | Capacity |
|---|---:|
| SS→A | 1 |
| SS→B | 1 |
| A→C | 1 |
| A→D | 1 |
| B→C | 1 |
| C→TT | 1 |
| D→TT | 1 |

Với thứ tự cạnh trên:
- Lần 1: `SS → A → C → TT`, Δ=1.
- Lần 2: `SS → B → C → A → D → TT`, Δ=1. Ở đây **C → A** là cung dư ngược, cho phép hủy luồng trên cạnh gốc A→C.
- Cuối: Max-Flow = 2; S={SS}; Min-Cut={SS→A, SS→B}, tổng Capacity=2.

## 5. Câu hỏi dễ bị vặn

- BFS khác DFS? BFS duyệt theo số cạnh, DFS đi sâu; Edmonds-Karp dùng BFS để đảm bảo O(VE²).
- Có thể bỏ cạnh ngược? Không; thiếu cơ chế hủy, phân bổ lại luồng.
- Vì sao Minimum Cut chứng minh tối ưu? Mọi luồng <= Capacity của mọi lát cắt; nếu tồn tại luồng có giá trị bằng một lát cắt thì nó là luồng cực đại.
- Làn rẽ phải Bắc ở SC05 có đi ngược chiều? Không. `LG_N_T → MOV_N_R` là kết nối làn chung, khác với cung dư ngược chỉ dùng nội bộ thuật toán.
