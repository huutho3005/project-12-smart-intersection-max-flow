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
    def __init__(self, page, scenario_id="SC02"):
        super().__init__("streamlit")
        self.page = page
        self.session_state = {"selected_sid": scenario_id}
        self.sidebar = self
        self.writes = []
        self.errors = []
        self.dataframes = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        return False

    def __getattr__(self, name):
        if name in {"title", "caption", "divider", "subheader", "code", "metric",
                    "info", "success", "dataframe", "plotly_chart", "download_button",
                    "set_page_config"}:
            return lambda *args, **kwargs: None
        raise AttributeError(name)

    def dataframe(self, data, *args, **kwargs):
        self.dataframes.append(data.copy())

    def write(self, text, *args, **kwargs):
        self.writes.append(str(text))

    def error(self, text, *args, **kwargs):
        self.errors.append(str(text))
        raise AssertionError("Giao diện báo lỗi: " + str(text))

    def stop(self):
        raise AssertionError("Giao diện dừng do lỗi")

    def radio(self, *_args, **_kwargs):
        return self.page

    def columns(self, count, **_kwargs):
        return [self] * int(count)

    def selectbox(self, _label, options, **_kwargs):
        return list(options)[0]

    def button(self, _label, **kwargs):
        return kwargs.get("key") == "run_ek"

    def expander(self, *_args, **_kwargs):
        return self

    def select_slider(self, _label, options, value=None, **_kwargs):
        return value if value is not None else list(options)[0]

    def checkbox(self, _label, value=False, **_kwargs):
        return value


class TestStreamlitPagesSmoke(unittest.TestCase):
    def execute_page(self, page, scenario_id="SC02"):
        fake = StreamlitStub(page, scenario_id)
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
