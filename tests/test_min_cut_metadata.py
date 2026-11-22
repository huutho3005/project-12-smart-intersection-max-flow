"""Kiểm thử phân loại lát cắt dựa trên trạng thái nhóm làn."""
import unittest
from ui_data import (run_scenario, cut_display_rows, cut_category,
                     cut_meaning, cut_partition_table)


class TestMinCutContext(unittest.TestCase):
    def test_sc05_e007_is_not_demand_bottleneck(self):
        result = run_scenario("SC05")
        row = next(x for x in cut_display_rows(result) if x["Edge ID"] == "E007")
        self.assertEqual(row["Capacity"], 0)
        self.assertEqual(row["Loại giới hạn"], "Nhóm làn không hoạt động (SC05)")
        self.assertIn("không phải điểm nghẽn", row["Ý nghĩa giao thông"])

    def test_e007_remains_demand_in_other_scenarios(self):
        for sid in ("SC01", "SC02", "SC03", "SC04"):
            with self.subTest(scenario=sid):
                result = run_scenario(sid)
                e007 = next(x for x in cut_display_rows(result)
                            if x["Edge ID"] == "E007")
                self.assertEqual(e007["Loại giới hạn"], "Giới hạn Demand")
                self.assertGreater(e007["Capacity"], 0)

    def test_zero_capacity_alone_is_not_inactive_lane(self):
        row = {"edge_id": "E007", "to": "LG_N_R", "from": "APP_N", "capacity": 0}
        lane_active = [{"lane_group_id": "LG_N_R", "is_active": "1"}]
        self.assertEqual(cut_category("E007", "SC05", row, lane_active),
                         "Giới hạn Demand")
        self.assertEqual(cut_category("E007", "SC05", row, []),
                         "Giới hạn Demand")
        self.assertEqual(cut_category("E007", "SC05", row,
                                      [{"lane_group_id": "LG_N_R", "is_active": "0"}]),
                         "Nhóm làn không hoạt động (SC05)")

    def test_cut_categories_dont_change_flow_or_cut_total(self):
        for sid in ("SC01", "SC02", "SC03", "SC04", "SC05"):
            with self.subTest(scenario=sid):
                result = run_scenario(sid)
                self.assertEqual(sum(x["Capacity"] for x in cut_display_rows(result)),
                                 result["min_cut"])
                self.assertEqual(result["max_flow"], result["min_cut"])

    def test_partition_uses_each_node_once(self):
        for sid in ("SC01", "SC02", "SC03", "SC04", "SC05"):
            with self.subTest(scenario=sid):
                result = run_scenario(sid)
                data = cut_partition_table(result)
                self.assertEqual(len(data), 2)
                left, right = data.values()
                self.assertEqual(set(filter(None, left)), set(result["S"]))
                self.assertEqual(set(filter(None, right)), set(result["T"]))
                self.assertEqual(len(list(filter(None, left))) +
                                 len(list(filter(None, right))), 34)


if __name__ == "__main__":
    unittest.main()
