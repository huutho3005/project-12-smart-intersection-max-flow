"""Giao diện Streamlit cho mô hình nút giao SMART INTERSECTION."""
import csv
from io import StringIO

import pandas as pd
import plotly.express as px
import streamlit as st

from ui_data import (scenario_catalog, run_scenario, run_all,
                     cut_display_rows, cut_partition_table, scenario_edge_changes)
from ui_graph import (graph_figure, residual_figure,
                      flow_from_residual_snapshot)

st.set_page_config(page_title="SMART INTERSECTION", page_icon="🚦",
                   layout="wide", initial_sidebar_state="expanded")

PAGE_NAMES = [
    "1. Tổng quan", "2. Mô hình", "3. Chọn Scenario",
    "4. Edmonds–Karp", "5. Minimum Cut", "6. So sánh",
]
SID_LABELS = {
    "SC01": "SC01 – Cơ sở",
    "SC02": "SC02 – Giờ cao điểm",
    "SC03": "SC03 – Suy giảm năng lực",
    "SC04": "SC04 – Bổ sung 2 làn quy đổi",
    "SC05": "SC05 – Điều chỉnh chức năng làn",
}


def as_csv(rows):
    if not rows:
        return ""
    buffer = StringIO()
    fields = list(rows[0])
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return "\ufeff" + buffer.getvalue()


def change_selected_scenario():
    st.session_state["selected_sid"] = st.session_state["sidebar_sid"]
    st.session_state.pop("run_result", None)


def choose_scenario(sid):
    st.session_state["selected_sid"] = sid
    st.session_state.pop("run_result", None)


def print_main_metrics(result):
    cols = st.columns(4)
    cols[0].metric("Demand", f'{result["demand"]:,} xe/giờ')
    cols[1].metric("Maximum Flow", f'{result["max_flow"]:,} xe/giờ')
    cols[2].metric("Minimum Cut", f'{result["min_cut"]:,} xe/giờ')
    cols[3].metric("Tỷ lệ đáp ứng", f'{result["satisfaction_pct"]:.2f}%')


def selected_result():
    saved = st.session_state.get("run_result")
    if saved and saved["scenario_id"] == st.session_state["selected_sid"]:
        return saved
    # Các trang xem mô hình / Min-Cut vẫn tự chạy thuật toán từ CSV hiện tại.
    return run_scenario(st.session_state["selected_sid"])


catalog = scenario_catalog()
ids = sorted(catalog)
if "selected_sid" not in st.session_state:
    st.session_state["selected_sid"] = "SC02" if "SC02" in catalog else ids[0]

with st.sidebar:
    st.title("🚦 SMART INTERSECTION")
    st.caption("Đề tài 12 · Cấu trúc rời rạc")
    page = st.radio("Đi đến trang", PAGE_NAMES, key="page_nav")
    st.divider()
    # Đồng bộ widget với nút chọn tại trang 3, nhưng không ghi đè dữ liệu mô hình.
    st.session_state["sidebar_sid"] = st.session_state["selected_sid"]
    st.selectbox("Kịch bản đang xem", ids,
                 format_func=lambda sid: SID_LABELS.get(sid, sid),
                 key="sidebar_sid", on_change=change_selected_scenario)
    st.caption("Nguồn dữ liệu: data/scenarios/SC01–SC05")
    st.caption("Thuật toán: Edmonds–Karp và Ford–Fulkerson")

sid = st.session_state["selected_sid"]

try:
    if page == PAGE_NAMES[0]:
        st.title("Tổng quan – SMART INTERSECTION")
        st.write("Mô hình hóa một nút giao bốn hướng bằng mạng luồng tĩnh. "
                 "Website phục vụ minh họa thuật toán, không phải hệ thống điều khiển đèn giao thông.")
        graph, movements, lanes, info = __import__("scenario").load_scenario(sid)
        m = st.columns(4)
        m[0].metric("Nodes", len(graph.nodes))
        m[1].metric("Edges gốc", len(graph.edges))
        m[2].metric("Movements", len(movements))
        m[3].metric("Scenarios", len(catalog))
        st.subheader("Quy trình tính toán")
        st.code("CSV → Kiểm tra dữ liệu → Mạng dư → BFS → Đường tăng → "
                "Bottleneck → Cập nhật Residual → Maximum Flow → Minimum Cut")
        st.subheader("Kịch bản đang chọn")
        st.write(f'**{SID_LABELS.get(sid,sid)}** – {info["description"]}')
        result = selected_result()
        print_main_metrics(result)
        st.info("Capacity/Demand dùng trong báo cáo là giả định mô phỏng. "
                "Mọi chỉ tiêu được tính từ CSV bằng thuật toán Python đã kiểm chứng.")

    elif page == PAGE_NAMES[1]:
        st.title("Mô hình – Đồ thị có hướng")
        result = selected_result()
        baseline = run_scenario("SC02")
        st.write("Đồ thị phân lớp: **SS → APP → LG → MOV → EXIT → TT**. "
                 "Chọn một trong bốn chế độ để xem dung lượng, luồng, mạng dư hoặc lát cắt.")
        direction_names = {"Tất cả":"Tất cả", "Bắc":"N", "Nam":"S", "Đông":"E", "Tây":"W"}
        selection = st.selectbox("Lọc theo hướng tiếp cận", list(direction_names), key="model_direction")
        sub = direction_names[selection]
        mode = st.radio("Chế độ trực quan hóa",
                        ["Capacity", "Flow/Capacity", "Residual", "Minimum Cut"],
                        horizontal=True, key="model_view_mode")
        compare = st.checkbox("So sánh với kịch bản tham chiếu SC02", value=(sid != "SC02"),
                              key="model_compare_sc02")
        changes = scenario_edge_changes(baseline["edges"], result["edges"])
        residual_step = None
        if mode == "Residual":
            if compare and sid != "SC02":
                available_steps = min(len(baseline["history"]), len(result["history"]))
            else:
                available_steps = len(result["history"])
            step_options = ["Trạng thái cuối"] + [f"Vòng {i}" for i in range(1, available_steps + 1)]
            residual_step = st.selectbox("Trạng thái mạng dư (dùng chung cho hai đồ thị)",
                                         step_options, key="residual_step_shared")

        def draw_model(target, label):
            st.markdown(f"**{label}**")
            flows = {e["edge_id"]: e["flow"] for e in target["edge_flows"]}
            if mode == "Residual":
                if residual_step == "Trạng thái cuối":
                    snapshot = target["residual_final"]
                else:
                    idx = int(residual_step.split()[-1]) - 1
                    snapshot = target["history"][idx]["residual_snapshot"]
                st.plotly_chart(residual_figure(target["nodes"], target["edges"], snapshot,
                                                 selected_direction=sub), use_container_width=True)
                st.caption("Cung dư thuận: nét liền xanh dương. Cung dư ngược: nét đứt tím. "
                           "Chỉ hiển thị các cung có Residual > 0.")
            else:
                cut_ids = [e["edge_id"] for e in target["cut_edges"]] if mode == "Minimum Cut" else []
                edge_states = scenario_edge_changes(baseline["edges"], target["edges"])
                fig = graph_figure(target["nodes"], target["edges"], selected_direction=sub,
                                   cut_ids=cut_ids, flows=flows, mode=mode,
                                   edge_states=edge_states)
                st.plotly_chart(fig, use_container_width=True)
                if mode == "Capacity":
                    st.caption("Xanh lá: Capacity tăng; vàng: giảm; tím: đổi kết nối; nét đứt: cạnh ngừng hoạt động.")
                elif mode == "Flow/Capacity":
                    st.caption("Nhãn trên cạnh thể hiện Flow/Capacity; cạnh bão hòa có Capacity dương được tô cam.")
                else:
                    st.caption("Cạnh đỏ thuộc một lát cắt tối thiểu của kịch bản đang xem.")

        if compare and sid != "SC02":
            col_a, col_b = st.columns(2)
            with col_a:
                draw_model(baseline, "SC02 – Kịch bản tham chiếu")
            with col_b:
                draw_model(result, f"{SID_LABELS.get(sid, sid)} – Kịch bản đang chọn")
        else:
            draw_model(result, SID_LABELS.get(sid, sid))

        changed_rows = []
        for edge_id, item in changes.items():
            if item["status"] != "unchanged":
                old_conn = "—" if item["old_connection"] is None else " → ".join(item["old_connection"])
                new_conn = "—" if item["new_connection"] is None else " → ".join(item["new_connection"])
                changed_rows.append({"Mã cạnh":edge_id, "Trạng thái":item["status"],
                                     "Kết nối SC02":old_conn, "Kết nối hiện tại":new_conn,
                                     "Capacity SC02":item["old_capacity"],
                                     "Capacity hiện tại":item["new_capacity"]})
        with st.expander("Xem các cạnh thay đổi so với SC02"):
            if changed_rows:
                st.dataframe(pd.DataFrame(changed_rows), hide_index=True, use_container_width=True)
            else:
                st.info("Không có cạnh thay đổi so với SC02.")
        with st.expander("Xem 44 cạnh và dung lượng dữ liệu gốc"):
            st.dataframe(pd.DataFrame([
                {"Mã cạnh":e["id"], "Đỉnh đầu":e["u"], "Đỉnh cuối":e["v"],
                 "Capacity":e["capacity"]} for e in result["edges"]
            ]), hide_index=True, use_container_width=True)
        st.caption("Mỗi đường vẽ là một cạnh gốc. Cung dư ngược là thao tác điều chỉnh luồng "
                   "trong thuật toán, không phải hướng xe chạy ngược chiều.")

    elif page == PAGE_NAMES[2]:
        st.title("Chọn Scenario – Dữ liệu đầu vào")
        st.write("Chọn một trong 5 kịch bản đã chuẩn hóa. "
                 "Mỗi kịch bản đọc **Edges + Lane_Groups + Movements** riêng.")
        cols = st.columns(5)
        for i, option in enumerate(ids):
            with cols[i]:
                st.button(SID_LABELS.get(option, option), use_container_width=True,
                          type="primary" if option == sid else "secondary",
                          key=f"choose_{option}", on_click=choose_scenario, args=(option,))
        sid = st.session_state["selected_sid"]
        graph, moves, lanes, info = __import__("scenario").load_scenario(sid)
        st.subheader(f'{SID_LABELS.get(sid,sid)}')
        st.write(info["description"])
        col1, col2, col3 = st.columns(3)
        col1.metric("Demand", f'{sum(int(m["demand_scenario"]) for m in moves):,}')
        col2.metric("Nhóm làn", len(lanes))
        col3.metric("Cạnh", len(graph.edges))
        baseline_graph, *_ = __import__("scenario").load_scenario("SC02")
        changes = scenario_edge_changes(baseline_graph.edges, graph.edges)
        changed_rows = []
        for edge_id, item in changes.items():
            if item["status"] != "unchanged":
                old_conn = "—" if item["old_connection"] is None else " → ".join(item["old_connection"])
                new_conn = "—" if item["new_connection"] is None else " → ".join(item["new_connection"])
                changed_rows.append({"Cạnh":edge_id, "Trạng thái":item["status"],
                                     "SC02 (đỉnh đầu → cuối)":old_conn,
                                     "Kịch bản này":new_conn,
                                     "Capacity SC02":item["old_capacity"],
                                     "Capacity hiện tại":item["new_capacity"]})
        st.subheader("Những thay đổi so với SC02")
        if changed_rows:
            st.dataframe(pd.DataFrame(changed_rows), hide_index=True, use_container_width=True)
        elif sid == "SC02":
            st.success("Đây là kịch bản tham chiếu SC02.")
        else:
            st.info("Dung lượng cạnh không đổi so với SC02; thay đổi Demand có thể thể hiện qua các cạnh đầu vào.")
        with st.expander("Metadata nhóm làn"):
            st.dataframe(pd.DataFrame(lanes)[["lane_group_id", "lane_count", "capacity_effective", "assigned_movements", "is_active"]],
                         hide_index=True, use_container_width=True)
        with st.expander("Metadata 12 chuyển động"):
            st.dataframe(pd.DataFrame(moves)[["movement_id", "lane_group_id", "exit_direction", "demand_scenario"]],
                         hide_index=True, use_container_width=True)
        st.caption("Demand cao điểm tổng cộng 8.932 là tổng sau làm tròn từng hướng/movement, "
                   "không lấy trực tiếp 6.870 × 1,30.")

    elif page == PAGE_NAMES[3]:
        st.title("Chạy Edmonds–Karp (BFS)")
        st.write(f'**Kịch bản:** {SID_LABELS.get(sid,sid)}')
        st.caption("BFS → đường tăng → bottleneck → cập nhật Residual → cộng luồng → BFS lại → STOP")
        if st.button("▶ Chạy thuật toán từ CSV", type="primary", key="run_ek"):
            st.session_state["run_result"] = run_scenario(sid)
        saved = st.session_state.get("run_result")
        if not saved or saved["scenario_id"] != sid:
            st.info("Nhấn **Chạy thuật toán từ CSV** để xem các vòng tăng luồng.")
        else:
            result = saved
            print_main_metrics(result)
            st.success(f'BFS đã kết thúc sau {len(result["history"])} lần tăng; '
                       f'Max-Flow = {result["max_flow"]:,} = Min-Cut = {result["min_cut"]:,}.')
            st.subheader("Nhật ký đường tăng luồng")
            history_rows = [{"Vòng":h["iteration"], "Đường tăng": " → ".join(h["path"]),
                             "Bottleneck":h["bottleneck"], "Max-Flow tạm thời":h["total_flow"]}
                            for h in result["history"]]
            st.dataframe(pd.DataFrame(history_rows), hide_index=True, use_container_width=True)
            st.download_button("Tải nhật ký đường tăng (CSV)", data=as_csv(history_rows),
                               file_name=f'{sid}_augmenting_paths.csv', mime="text/csv")
            steps = result["history"]
            if steps:
                st.subheader("Phát lại từng vòng")
                iteration = st.select_slider("Vòng tăng luồng", options=[h["iteration"] for h in steps],
                                             value=steps[0]["iteration"], key=f"step_selected_{sid}")
                step = next(h for h in steps if h["iteration"] == iteration)
                st.write(f'**Iteration {iteration}:** `{" → ".join(step["path"])}`')
                a, b = st.columns(2)
                a.metric("Bottleneck Δ", step["bottleneck"])
                b.metric("Tổng luồng sau vòng", step["total_flow"])
                st.write("**Những cung dư BFS thực sự chọn:**")
                arc_rows = [{"Cạnh gốc":a["edge_id"], "Loại cung dư":a["arc_type"],
                             "Đi từ":a["from"], "Đến":a["to"],
                             "Chỉ số cung":a["arc_index"]} for a in step["path_arcs"]]
                st.dataframe(pd.DataFrame(arc_rows), hide_index=True, use_container_width=True)
                flows = flow_from_residual_snapshot(result["edges"], step["residual_snapshot"])
                st.plotly_chart(graph_figure(result["nodes"], result["edges"],
                                             path_arcs=step["path_arcs"],
                                             flows=flows, mode="Capacity"), use_container_width=True)
                st.caption("Đường cam nét liền: cung dư thuận; cam nét đứt: cung dư ngược. "
                           "Mũi tên màu cam là chiều BFS thực sự đi trên mạng dư, "
                           "không nhất thiết trùng chiều cạnh gốc.")
                with st.expander("Mạng dư SAU vòng này (88 cung thuận/ngược)"):
                    only_positive = st.checkbox("Chỉ xem Residual > 0", value=True)
                    rows = step["residual_snapshot"]
                    if only_positive:
                        rows = [x for x in rows if x["residual"] > 0]
                    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
                st.caption("Cung 'reverse' là thao tác hủy/điều chỉnh luồng cũ, "
                           "không phải cho xe chạy ngược chiều.")

    elif page == PAGE_NAMES[4]:
        st.title("Minimum Cut – Giới hạn lưu lượng")
        result = selected_result()
        print_main_metrics(result)
        st.write("Tập S là các đỉnh còn tới được từ SS qua cạnh dư có dung lượng dương; "
                 "T là phần còn lại. Các cạnh gốc đi từ S sang T tạo lát cắt.")
        st.subheader(f'Tập đỉnh S ({len(result["S"])} đỉnh) và T ({len(result["T"])} đỉnh)')
        st.caption("Mỗi đỉnh nằm trên một dòng; cuộn dọc nếu danh sách dài. "
                   "Hai cột biểu diễn hai phía của lát cắt, không phải cặp đỉnh nối nhau.")
        st.dataframe(pd.DataFrame(cut_partition_table(result)),
                     hide_index=True, use_container_width=True,
                     height=min(38 * max(len(result["S"]), len(result["T"])) + 38, 700))
        cut_rows = cut_display_rows(result)
        st.subheader("Các cạnh thuộc lát cắt tối thiểu")
        st.dataframe(pd.DataFrame(cut_rows), hide_index=True, use_container_width=True)
        st.write(f'**Tổng dung lượng lát cắt = {sum(e["Capacity"] for e in cut_rows):,} xe/giờ.**')
        st.success("Đạt kiểm chứng: Maximum Flow = Minimum Cut")
        st.plotly_chart(graph_figure(result["nodes"], result["edges"],
                                     cut_ids=[e["edge_id"] for e in result["cut_edges"]],
                                     flows={e["edge_id"]:e["flow"] for e in result["edge_flows"]},
                                     mode="Minimum Cut"), use_container_width=True)
        st.caption("Đường màu đỏ là cạnh thuộc một lát cắt tối thiểu. Cạnh giới hạn Demand "
                   "không đồng nghĩa với điểm ùn tắc hạ tầng. Trong SC05, E007=0 "
                   "được phân loại riêng là nhóm làn LG_N_R không hoạt động.")

    elif page == PAGE_NAMES[5]:
        st.title("So sánh 5 Scenario")
        results = run_all()
        rows = [{"Scenario":r["scenario_id"], "Demand":r["demand"],
                 "Max Flow (BFS)":r["max_flow"], "Max Flow (DFS)":r["dfs_flow"],
                 "Min Cut":r["min_cut"], "Chưa phục vụ":r["unserved"],
                 "Đáp ứng (%)":round(r["satisfaction_pct"], 2),
                 "Lần tăng BFS":len(r["history"]), "Lần tăng DFS":len(r["dfs_history"])}
                for r in results]
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
        st.download_button("Tải bảng đối chiếu (CSV)", data=as_csv(rows),
                           file_name="SMART_INTERSECTION_5_scenarios.csv", mime="text/csv")
        fig = px.bar(pd.DataFrame(rows), x="Scenario", y="Max Flow (BFS)",
                     text="Max Flow (BFS)", labels={"Max Flow (BFS)":"Xe quy ước/giờ"})
        fig.update_traces(textposition="outside")
        fig.update_layout(height=410, margin=dict(l=10,r=10,t=25,b=10))
        st.plotly_chart(fig, use_container_width=True)
        baseline = next(r for r in results if r["scenario_id"] == "SC02")
        rows_delta = []
        for r in results:
            if r["scenario_id"] == "SC02":
                continue
            diff = r["max_flow"] - baseline["max_flow"]
            rows_delta.append({"Scenario":r["scenario_id"],
                               "Chênh lệch so với SC02":diff,
                               "Biến động (%)":round(100*diff/baseline["max_flow"],2)})
        st.subheader("Biến động so với giờ cao điểm SC02")
        st.dataframe(pd.DataFrame(rows_delta), hide_index=True, use_container_width=True)
        st.success("BFS = DFS = Min-Cut trong cả 5 kịch bản")
        st.caption("Các giá trị được tính lại từ Edges.csv riêng của từng scenario, "
                   "không gán sẵn trong trang web.")
except (ValueError, AssertionError, OSError, KeyError) as error:
    st.error(f"Không thể đọc hoặc kiểm chứng dữ liệu: {error}")
    st.stop()
