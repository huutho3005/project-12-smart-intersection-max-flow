"""Trực quan hóa đồ thị gốc và mạng dư; không tính lại luồng."""
import plotly.graph_objects as go

DIRECTIONS = ("N", "S", "E", "W")
NODE_COLORS = {
    "SS": "#183a69", "APP": "#1d85a6", "LG": "#e6a443",
    "MOV": "#8757b3", "EXIT": "#23866e", "TT": "#183a69",
}
MODE_COLORS = {
    "unchanged": "#94a3b8", "increased": "#15966b",
    "decreased": "#e5a12b", "connection_changed": "#8757b3",
    "inactive": "#64748b", "added": "#15966b", "removed": "#64748b",
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


def _edge_style(edge, mode, edge_states, cut_ids, path_ids, flows):
    eid = edge["id"]
    cap = edge["capacity"]
    flow = flows.get(eid)
    # Trạng thái tô nổi bật có ưu tiên cao hơn màu Capacity/Flow mặc định.
    # Trên trang Minimum Cut: chỉ các cạnh thuộc cut mới được tô đỏ.
    if mode == "Minimum Cut":
        if eid in cut_ids:
            return "#d64141", 3.6, "solid"
        return "#94a3b8", 1.2, "solid"
    # Trang phát lại truyền path_ids nhưng dùng chế độ Capacity mặc định.
    # Bắt buộc ưu tiên đường tăng trước khi xét Capacity/Flow saturation.
    if eid in path_ids:
        return "#eb9634", 3.4, "solid"
    if mode == "Capacity":
        state = (edge_states or {}).get(eid, {}).get("status", "unchanged")
        color = MODE_COLORS.get(state, MODE_COLORS["unchanged"])
        dash = "dash" if state == "inactive" else "solid"
        width = 3.0 if state != "unchanged" else 1.5
        return color, width, dash
    if mode == "Flow/Capacity":
        if cap == 0:
            return MODE_COLORS["inactive"], 1.6, "dash"
        if flow is not None and flow >= cap:
            return "#e87924", 3.2, "solid"
        return "#3986b8", 1.7, "solid"
    if eid in cut_ids:
        return "#d64141", 3.4, "solid"
    return "#94a3b8", 1.4, "solid"


def graph_figure(nodes, edges, selected_direction="Tất cả", cut_ids=(), path_ids=(),
                 flows=None, mode="Capacity", edge_states=None, path_arcs=None):
    """Vẽ đồ thị gốc; với path_arcs, vẽ thêm các cung dư đúng chiều BFS.

    path_ids được giữ cho các lời gọi cũ chỉ tô cạnh gốc. Khi có path_arcs,
    nét liền cam là cung thuận và nét đứt cam là cung dư ngược; mũi tên cam
    mang chiều từ arc["from"] tới arc["to"], KHÔNG suy ra từ cạnh gốc.
    """
    shown = filter_graph_edges(edges, selected_direction)
    coords = positions(nodes)
    visible_nodes = {v for e in shown for v in (e["u"], e["v"])}
    cut_ids, path_ids = set(cut_ids), set(path_ids)
    flows = flows or {}
    arcs = list(path_arcs or ())
    edge_by_id = {edge["id"]: edge for edge in edges}
    for arc in arcs:
        eid = arc["edge_id"]
        if eid not in edge_by_id:
            raise ValueError(f"Cung dư tham chiếu mã cạnh không tồn tại: {eid}")
        original = edge_by_id[eid]
        if arc["arc_type"] == "forward":
            expected = (original["u"], original["v"])
        elif arc["arc_type"] == "reverse":
            expected = (original["v"], original["u"])
        else:
            raise ValueError(f"Loại cung dư không hợp lệ: {arc['arc_type']}")
        if (arc["from"], arc["to"]) != expected:
            raise ValueError(f"Chiều cung dư {eid} không khớp cạnh gốc: {arc}")
    # Nếu có path_arcs: nền giữ màu mô hình, phần tô cam do cung dư phía trên vẽ.
    # Không tô cạnh gốc cam, vì có thể gây hiểu sai chiều cung dư ngược.
    oriented_ids = {arc["edge_id"] for arc in arcs}
    shown_ids = {e["id"] for e in shown}
    base_path_ids = () if arcs else path_ids
    fig = go.Figure()
    hx, hy, htext = [], [], []
    lx, ly, ltext = [], [], []
    for edge in shown:
        u, v = edge["u"], edge["v"]
        x0, y0 = coords[u]
        x1, y1 = coords[v]
        eid = edge["id"]
        color, width, dash = _edge_style(edge, mode, edge_states, cut_ids, base_path_ids, flows)
        fig.add_trace(go.Scatter(
            x=[x0, x1], y=[y0, y1], mode="lines",
            line=dict(color=color, width=width, dash=dash),
            hoverinfo="skip", showlegend=False))
        xstart, ystart = x0 + 0.42*(x1-x0), y0 + 0.42*(y1-y0)
        xend, yend = x0 + 0.62*(x1-x0), y0 + 0.62*(y1-y0)
        # Khi cung thuộc đường phát lại, chỉ vẽ mũi tên cam có chiều thực tế.
        # Bỏ mũi tên cạnh gốc để không có hai mũi tên ngược nhau gây nhầm lẫn.
        if eid not in oriented_ids:
            fig.add_annotation(x=xend, y=yend, ax=xstart, ay=ystart,
                               xref="x", yref="y", axref="x", ayref="y",
                               showarrow=True, arrowhead=2, arrowsize=0.65,
                               arrowwidth=1.2, arrowcolor=color)
        hx.append((x0+x1)/2)
        hy.append((y0+y1)/2)
        flow = flows.get(eid)
        label = f"<b>{eid}</b>: {u} → {v}<br>Capacity: {edge['capacity']:,}"
        if flow is not None:
            label += f"<br>Flow: {flow:,}<br>Flow/Capacity: {flow:,}/{edge['capacity']:,}"
        if mode == "Capacity" and edge_states and eid in edge_states:
            label += f"<br>Thay đổi: {edge_states[eid]['status']}"
        htext.append(label)
        if mode == "Flow/Capacity":
            lx.append((x0+x1)/2)
            ly.append((y0+y1)/2 + 0.18)
            ltext.append(f"{flow if flow is not None else 0:,}/{edge['capacity']:,}")
        elif mode == "Capacity":
            lx.append((x0+x1)/2)
            ly.append((y0+y1)/2 + 0.18)
            ltext.append(f"{edge['capacity']:,}")

    # Đường tăng luồng: vẽ cung dư riêng, đúng chiều BFS ở từng vòng.
    # Nét đứt cam biểu thị hoàn tác luồng trên cạnh gốc; không phải xe đi ngược.
    for arc in arcs:
        eid = arc["edge_id"]
        if eid not in shown_ids:
            continue
        original = edge_by_id[eid]
        x0, y0 = coords[arc["from"]]
        x1, y1 = coords[arc["to"]]
        is_reverse = arc["arc_type"] == "reverse"
        if is_reverse:
            # Dịch nhẹ cung ngược khỏi cạnh gốc, giữ rõ nét đứt và chiều đi.
            dx = coords[original["v"]][0] - coords[original["u"]][0]
            dy = coords[original["v"]][1] - coords[original["u"]][1]
            length = (dx*dx + dy*dy) ** 0.5 or 1.0
            offset_x, offset_y = -dy / length * 0.13, dx / length * 0.13
            x0 += offset_x
            x1 += offset_x
            y0 += offset_y
            y1 += offset_y
        color = "#eb9634"
        fig.add_trace(go.Scatter(
            x=[x0, x1], y=[y0, y1], mode="lines",
            line=dict(color=color, width=4.1, dash="dash" if is_reverse else "solid"),
            hoverinfo="skip", showlegend=False))
        fig.add_annotation(
            x=x0+0.64*(x1-x0), y=y0+0.64*(y1-y0),
            ax=x0+0.40*(x1-x0), ay=y0+0.40*(y1-y0),
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=3, arrowsize=1.1,
            arrowwidth=2.6, arrowcolor=color)
        hx.append((x0+x1)/2)
        hy.append((y0+y1)/2)
        arc_label = "cung dư ngược" if is_reverse else "cung dư thuận"
        htext.append(f"<b>{eid}</b> · {arc_label}<br>"
                     f"BFS: {arc['from']} → {arc['to']}")

    fig.add_trace(go.Scatter(
        x=hx, y=hy, mode="markers", marker=dict(size=10, opacity=0),
        text=htext, hovertemplate="%{text}<extra></extra>", showlegend=False,
    ))
    if ltext:
        fig.add_trace(go.Scatter(
            x=lx, y=ly, mode="text", text=ltext,
            textfont=dict(size=8, color="#334155"),
            hoverinfo="skip", showlegend=False,
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


def residual_figure(nodes, edges, residual_arcs, selected_direction="Tất cả"):
    """Hiển thị các cung dư dương; thuận nét liền xanh, ngược nét đứt tím."""
    coords = positions(nodes)
    shown_edges = filter_graph_edges(edges, selected_direction)
    shown_ids = {e["id"] for e in shown_edges}
    edge_by_id = {e["id"]: e for e in edges}
    visible_nodes = {v for e in shown_edges for v in (e["u"], e["v"])}
    fig = go.Figure()
    hx, hy, htext = [], [], []
    for arc in residual_arcs:
        if arc["edge_id"] not in shown_ids or int(arc["residual"]) <= 0:
            continue
        original = edge_by_id[arc["edge_id"]]
        ux, uy = coords[original["u"]]
        vx, vy = coords[original["v"]]
        dx, dy = vx-ux, vy-uy
        length = (dx*dx + dy*dy) ** 0.5 or 1.0
        nx, ny = -dy/length, dx/length
        side = 0.16 if arc["arc_type"] == "forward" else -0.16
        x0, y0 = coords[arc["from"]]
        x1, y1 = coords[arc["to"]]
        x0, y0 = x0 + nx*side, y0 + ny*side
        x1, y1 = x1 + nx*side, y1 + ny*side
        color = "#2878bd" if arc["arc_type"] == "forward" else "#8757b3"
        dash = "solid" if arc["arc_type"] == "forward" else "dash"
        fig.add_trace(go.Scatter(x=[x0,x1], y=[y0,y1], mode="lines",
                                 line=dict(color=color, width=2.0, dash=dash),
                                 hoverinfo="skip", showlegend=False))
        fig.add_annotation(x=x0+0.62*(x1-x0), y=y0+0.62*(y1-y0),
                           ax=x0+0.42*(x1-x0), ay=y0+0.42*(y1-y0),
                           xref="x", yref="y", axref="x", ayref="y",
                           showarrow=True, arrowhead=2, arrowsize=0.65,
                           arrowwidth=1.1, arrowcolor=color)
        hx.append((x0+x1)/2); hy.append((y0+y1)/2)
        htext.append(f"<b>{arc['edge_id']}</b> · {arc['arc_type']}<br>"
                     f"{arc['from']} → {arc['to']}<br>Residual: {arc['residual']:,}")
    fig.add_trace(go.Scatter(x=hx, y=hy, mode="markers",
                             marker=dict(size=10, opacity=0), text=htext,
                             hovertemplate="%{text}<extra></extra>", showlegend=False))
    for group in ("SS", "APP", "LG", "MOV", "EXIT", "TT"):
        members = [n for n in visible_nodes if node_group(n) == group]
        if members:
            fig.add_trace(go.Scatter(
                x=[coords[n][0] for n in members], y=[coords[n][1] for n in members],
                mode="markers+text", text=members, textposition="top center",
                textfont=dict(size=10), name=group,
                marker=dict(size=13, color=NODE_COLORS[group], line=dict(width=1, color="#ffffff")),
                hovertemplate="<b>%{text}</b><extra></extra>"))
    fig.update_layout(height=670 if selected_direction == "Tất cả" else 460,
                      xaxis=dict(visible=False, range=[-0.5,10.5]),
                      yaxis=dict(visible=False, range=[-1,12.5]),
                      margin=dict(l=10,r=10,t=30,b=12),
                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                      hovermode="closest")
    return fig


def flow_from_residual_snapshot(edges, snapshot):
    """Tái dựng luồng qua cạnh gốc ở một iteration, không cần chạy lại thuật toán."""
    forward = {a["edge_id"]: a["residual"] for a in snapshot
               if a["arc_type"] == "forward"}
    return {e["id"]: e["capacity"] - forward[e["id"]] for e in edges}
