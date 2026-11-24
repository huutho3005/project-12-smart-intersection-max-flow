"""Kiểm thử khói đường thực thi 6 trang bằng Streamlit giả lập (không cần server).

Mục tiêu: bắt lỗi khi trang dùng sai khóa dữ liệu, như "Capacity" / "capacity".
KHÔNG thay thế kiểm tra thao tác và trình duyệt Streamlit thật.
"""
from pathlib import Path

# Nap pandas truoc khi mock sys.modules: tranh lazy-import NumPy/Pandas khi stub Streamlit dang duoc patch.
import pandas as pd
import runpy
import sys
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    "1. Tổng quan", "2. Mô hình", "3. Chọn Scenario",
    "4. Edmonds–Karp", "5. Minimum Cut", "6. So sánh",
]


class StreamlitStub(types.ModuleType):
    def __init__(self, page, scenario_id="SC02", model_mode=None):
        super().__init__("streamlit")
        self.page = page
        self.model_mode = model_mode
        self.session_state = {"selected_sid": scenario_id}
        self.sidebar = self
        self.writes = []
        self.errors = []
        self.dataframes = []
        self.plotly_line_colors = []
        self.plotly_figures = []
        self.replay_iteration = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        return False

    def __getattr__(self, name):
        if name in {"title", "caption", "divider", "subheader", "code", "metric",
                    "info", "success", "dataframe", "plotly_chart", "download_button",
                    "set_page_config", "markdown"}:
            return lambda *args, **kwargs: None
        raise AttributeError(name)

    def dataframe(self, data, *args, **kwargs):
        self.dataframes.append(data.copy())

    def plotly_chart(self, figure, *args, **kwargs):
        # Kiểm tra đúng dữ liệu được trang app.py gửi cho Plotly, không chỉ kiểm tra không lỗi.
        self.plotly_figures.append(figure.to_plotly_json())
        self.plotly_line_colors.append([getattr(getattr(trace, "line", None), "color", None) for trace in figure.data])

    def write(self, text, *args, **kwargs):
        self.writes.append(str(text))

    def error(self, text, *args, **kwargs):
        self.errors.append(str(text))
        raise AssertionError("Giao diện báo lỗi: " + str(text))

    def stop(self):
        raise AssertionError("Giao diện dừng do lỗi")

    def radio(self, label, options, **_kwargs):
        if label == "Đi đến trang":
            return self.page
        if label == "Chế độ trực quan hóa" and self.model_mode:
            return self.model_mode
        return list(options)[0]

    def columns(self, count, **_kwargs):
        return [self] * int(count)

    def selectbox(self, _label, options, **_kwargs):
        return list(options)[0]

    def button(self, _label, **kwargs):
        return kwargs.get("key") == "run_ek"

    def expander(self, *_args, **_kwargs):
        return self

    def select_slider(self, _label, options, value=None, **_kwargs):
        if self.replay_iteration is not None and self.replay_iteration in options:
            return self.replay_iteration
        return value if value is not None else list(options)[0]

    def checkbox(self, _label, value=False, **_kwargs):
        return value


class TestStreamlitPagesSmoke(unittest.TestCase):
    def execute_page(self, page, scenario_id="SC02", model_mode=None, replay_iteration=None):
        fake = StreamlitStub(page, scenario_id, model_mode=model_mode)
        fake.replay_iteration = replay_iteration
        # Thực thi TOÀN BỘ app.py với API Streamlit thay bằng stub;
        # do đó phát hiện được lỗi truy cập dictionary trong UI.
        with patch.dict(sys.modules, {"streamlit": fake}):
            runpy.run_path(str(ROOT / "app.py"), run_name="__smoke_test__")
        self.assertEqual(fake.errors, [])
        return fake

    def test_all_six_pages_no_python_exception(self):
        for page in PAGES:
            with self.subTest(page=page):
                self.execute_page(page)


    def test_edmonds_karp_replay_marks_selected_residual_arcs_orange(self):
        from ui_data import run_scenario
        result = run_scenario("SC01")
        fake = self.execute_page(PAGES[3], "SC01")
        self.assertEqual(len(fake.plotly_figures), 1)
        fig = fake.plotly_figures[0]
        arcs = result["history"][0]["path_arcs"]
        n = len(result["edges"])
        # Cạnh gốc nằm phía dưới, không mang mũi tên màu cam sai chiều.
        self.assertEqual({fig["data"][i]["line"]["color"] for i in range(n)}, {"#94a3b8"})
        # Các cung dư được vẽ thành một lớp riêng, theo đúng thứ tự BFS chọn.
        overlays = fig["data"][n:n+len(arcs)]
        self.assertEqual(len(overlays), len(arcs))
        self.assertTrue(all(t["line"]["color"] == "#eb9634" for t in overlays))
        self.assertTrue(all(t["line"]["dash"] == "solid" for t in overlays))

    def test_sc05_iteration_13_draws_two_reverse_arrows(self):
        from ui_data import run_scenario
        from ui_graph import positions
        result = run_scenario("SC05")
        step = result["history"][12]
        self.assertEqual(step["iteration"], 13)
        self.assertEqual(step["bottleneck"], 45)
        self.assertEqual([a["edge_id"] for a in step["path_arcs"] if a["arc_type"] == "reverse"],
                         ["E030", "E018"])
        fake = self.execute_page(PAGES[3], "SC05", replay_iteration=13)
        fig = fake.plotly_figures[0]
        n = len(result["edges"])
        overlays = fig["data"][n:n+len(step["path_arcs"])]
        for arc, trace, arrow in zip(step["path_arcs"], overlays,
                                     fig["layout"]["annotations"][-len(step["path_arcs"]):]):
            self.assertEqual(trace["line"]["color"], "#eb9634")
            self.assertEqual(trace["line"]["dash"],
                             "dash" if arc["arc_type"] == "reverse" else "solid")
            self.assertEqual(arrow["arrowcolor"], "#eb9634")
            x0, y0 = positions(result["nodes"])[arc["from"]]
            x1, y1 = positions(result["nodes"])[arc["to"]]
            dot = (arrow["x"]-arrow["ax"])*(x1-x0)+(arrow["y"]-arrow["ay"])*(y1-y0)
            self.assertGreater(dot, 0, msg=arc["edge_id"])
        reverse = {a["edge_id"]:(a["from"], a["to"])
                   for a in step["path_arcs"] if a["arc_type"] == "reverse"}
        self.assertEqual(reverse, {"E030":("EXIT_S","MOV_N_T"),
                                   "E018":("MOV_N_T","LG_N_T")})

    def test_min_cut_page_marks_exact_cut_edges_red(self):
        from ui_data import run_scenario
        result = run_scenario("SC05")
        fake = self.execute_page(PAGES[4], "SC05")
        self.assertEqual(len(fake.plotly_line_colors), 1)
        colors_of_traces = fake.plotly_line_colors[0]
        cut_ids = {e["edge_id"] for e in result["cut_edges"]}
        colors = {e["id"]: colors_of_traces[i]
                  for i, e in enumerate(result["edges"])}
        self.assertEqual(len(colors), 44)
        self.assertEqual({eid for eid, color in colors.items() if color == "#d64141"}, cut_ids)
        self.assertEqual({eid for eid, color in colors.items() if color == "#94a3b8"},
                         set(colors) - cut_ids)
        self.assertIn("E007", cut_ids)  # Cạnh capacity 0 vẫn thuộc lát cắt theo S/T.

    def test_model_page_renders_side_by_side_scenario_comparison(self):
        fake = self.execute_page(PAGES[1], "SC05", model_mode="Flow/Capacity")
        # Hai đồ thị: SC02 tham chiếu và SC05 đang chọn.
        self.assertGreaterEqual(len(fake.writes), 0)
        self.assertEqual(fake.errors, [])

    def test_model_page_supports_residual_mode(self):
        fake = self.execute_page(PAGES[1], "SC05", model_mode="Residual")
        self.assertEqual(fake.errors, [])

    def test_min_cut_capacity_for_all_five_scenarios(self):
        from ui_data import run_scenario
        for scenario_id in ["SC01", "SC02", "SC03", "SC04", "SC05"]:
            with self.subTest(scenario=scenario_id):
                expected = run_scenario(scenario_id)["min_cut"]
                rendered = self.execute_page(PAGES[4], scenario_id)
                totals = [line for line in rendered.writes if "Tổng dung lượng lát cắt" in line]
                self.assertEqual(len(totals), 1)
                self.assertIn(f"{expected:,}", totals[0])

    def test_min_cut_sc05_inactive_lane_is_labeled_in_rendered_table(self):
        fake = self.execute_page(PAGES[4], "SC05")
        cut_tables = [df for df in fake.dataframes if "Loại giới hạn" in df.columns]
        self.assertEqual(len(cut_tables), 1)
        row = cut_tables[0].loc[cut_tables[0]["Edge ID"] == "E007"].iloc[0]
        self.assertEqual(int(row["Capacity"]), 0)
        self.assertEqual(row["Loại giới hạn"], "Nhóm làn không hoạt động (SC05)")
        self.assertNotEqual(row["Loại giới hạn"], "Giới hạn Demand")
        self.assertIn("LG_N_R", row["Ý nghĩa giao thông"])

    def test_min_cut_st_sets_are_complete_and_in_two_columns(self):
        from ui_data import run_scenario
        for sid in ["SC01", "SC02", "SC03", "SC04", "SC05"]:
            with self.subTest(scenario=sid):
                fake = self.execute_page(PAGES[4], sid)
                tables = [df for df in fake.dataframes
                          if any(str(k).startswith("Tập S (") for k in df.columns)]
                self.assertEqual(len(tables), 1)
                table = tables[0]
                self.assertEqual(len(table.columns), 2)
                displayed = {str(x) for col in table.columns for x in table[col] if x}
                result = run_scenario(sid)
                self.assertEqual(displayed, set(result["S"]) | set(result["T"]))
                self.assertEqual(set(result["S"]) & set(result["T"]), set())
                self.assertEqual(len(displayed), 34)



if __name__ == "__main__":
    unittest.main()
