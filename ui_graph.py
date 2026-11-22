"""Chỉ trực quan hóa 34 đỉnh, 44 cạnh GỐC; không tính lại luồng."""
import plotly.graph_objects as go

DIRECTIONS = ("N", "S", "E", "W")
NODE_COLORS = {
    "SS": "#183a69", "APP": "#1d85a6", "LG": "#e6a443",
    "MOV": "#8757b3", "EXIT": "#23866e", "TT": "#183a69",
}


def node_group(name):
    if name in ("SS", "TT"):
        return name
    return name.split("_")[0]


def positions(nodes):
    """Vị trí cố định theo sáu lớp SS -> APP -> LG -> MOV -> EXIT -> TT."""
    result = {"SS": (0.0, 5.8), "TT": (10.0, 5.8)}
    ys = {"N": 11.0, "S": 7.8, "E": 4.6, "W": 1.4}
    for direction in DIRECTIONS:
        if "APP_" + direction in nodes:
            result["APP_" + direction] = (1.8, ys[direction])
        if "EXIT_" + direction in nodes:
            result["EXIT_" + direction] = (8.2, ys[direction])
        for code, offset in (("L", 0.85), ("T", 0), ("R", -0.85)):
            for prefix, x in (("LG", 3.6), ("MOV", 5.7)):
                nid = f"{prefix}_{direction}_{code}"
                if nid in nodes:
                    result[nid] = (x, ys[direction] + offset)
    return result


def filter_graph_edges(edges, selected_direction):
    if selected_direction == "Tất cả":
        return list(edges)
    direction = selected_direction
    prefix = f"_{direction}_"
    chosen = [e for e in edges if (
        (e["u"] == "SS" and e["v"] == "APP_" + direction)
        or (e["u"] == "APP_" + direction and e["v"].startswith("LG" + prefix))
        or (e["u"].startswith("LG" + prefix) and e["v"].startswith("MOV" + prefix))
        or e["u"].startswith("MOV" + prefix)
    )]
    exits = {e["v"] for e in chosen if e["v"].startswith("EXIT_")}
    chosen += [e for e in edges if e["u"] in exits and e["v"] == "TT"]
    return chosen


def graph_figure(nodes, edges, selected_direction="Tất cả", cut_ids=(), path_ids=(), flows=None):
    """Đồ thị lớp; hover xem từng cạnh, Capacity, Flow và loại cạnh.

    `flows` là dict edge_id->Flow có thể lấy tại một iteration từ snapshot dư.
    """
    shown = filter_graph_edges(edges, selected_direction)
    coords = positions(nodes)
    visible_nodes = {v for e in shown for v in (e["u"], e["v"])}
    cut_ids, path_ids = set(cut_ids), set(path_ids)
    flows = flows or {}
    fig = go.Figure()

    hx, hy, htext = [], [], []
    for edge in shown:
        u, v = edge["u"], edge["v"]
        x0, y0 = coords[u]
        x1, y1 = coords[v]
        eid = edge["id"]
        color = "#d64141" if eid in cut_ids else "#eb9634" if eid in path_ids else "#94a3b8"
        width = 3.4 if eid in cut_ids or eid in path_ids else 1.4
        fig.add_trace(go.Scatter(
            x=[x0, x1], y=[y0, y1], mode="lines",
            line=dict(color=color, width=width),
            hoverinfo="skip", showlegend=False))
        # Mũi tên nằm giữa cạnh để biểu thị CHIỀU giao thông gốc.
        # Đặt gần giữa thay vì sát nút nhằm tránh che nhãn đỉnh.
        xstart, ystart = x0 + 0.42*(x1-x0), y0 + 0.42*(y1-y0)
        xend, yend = x0 + 0.62*(x1-x0), y0 + 0.62*(y1-y0)
        fig.add_annotation(x=xend, y=yend, ax=xstart, ay=ystart,
                           xref="x", yref="y", axref="x", ayref="y",
                           showarrow=True, arrowhead=2, arrowsize=0.65,
                           arrowwidth=1.2, arrowcolor=color)
        hx.append((x0+x1)/2)
        hy.append((y0+y1)/2)
        label = (f"<b>{eid}</b>: {u} → {v}<br>Capacity: {edge['capacity']:,}"
                 + (f"<br>Flow: {flows[eid]:,}" if eid in flows else ""))
        htext.append(label)

    fig.add_trace(go.Scatter(
        x=hx, y=hy, mode="markers", marker=dict(size=10, opacity=0),
        text=htext, hovertemplate="%{text}<extra></extra>", showlegend=False,
    ))
    for group in ("SS", "APP", "LG", "MOV", "EXIT", "TT"):
        members = [n for n in visible_nodes if node_group(n) == group]
        if not members:
            continue
        fig.add_trace(go.Scatter(
            x=[coords[n][0] for n in members], y=[coords[n][1] for n in members],
            mode="markers+text", text=members, textposition="top center",
            textfont=dict(size=10), name=group,
            marker=dict(size=13, color=NODE_COLORS[group], line=dict(width=1, color="#ffffff")),
            hovertemplate="<b>%{text}</b><extra></extra>",
        ))
    fig.update_layout(
        height=670 if selected_direction == "Tất cả" else 460,
        xaxis=dict(visible=False, range=[-0.5,10.5]),
        yaxis=dict(visible=False, range=[-1,12.5]),
        margin=dict(l=10, r=10, t=30, b=12),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        hovermode="closest", legend=dict(orientation="h", y=-0.02, x=0.05),
    )
    return fig


def flow_from_residual_snapshot(edges, snapshot):
    """Tái dựng luồng qua cạnh gốc ở một iteration, không cần chạy lại thuật toán."""
    forward = {a["edge_id"]: a["residual"] for a in snapshot
               if a["arc_type"] == "forward"}
    return {e["id"]: e["capacity"] - forward[e["id"]] for e in edges}
