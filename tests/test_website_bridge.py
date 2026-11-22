"""Kiểm thử giao diện ở lớp tính toán; KHÔNG thay cho chạy trình duyệt Streamlit."""
import unittest
from ui_data import run_all, run_scenario, cut_meaning
from ui_graph import graph_figure, flow_from_residual_snapshot, filter_graph_edges


class TestWebsiteBridge(unittest.TestCase):
    def test_six_pages_use_real_five_scenario_results(self):
        expected = {"SC01": 6511, "SC02": 7145, "SC03": 6073,
                    "SC04": 7708, "SC05": 7401}
        for result in run_all():
            sid = result["scenario_id"]
            self.assertEqual(result["max_flow"], expected[sid])
            self.assertEqual(result["max_flow"], result["dfs_flow"])
            self.assertEqual(result["max_flow"], result["min_cut"])
            self.assertEqual(len(result["edges"]), 44)
            self.assertEqual(len(result["nodes"]), 34)
            self.assertEqual(len(result["movements"]), 12)

    def test_each_iteration_has_its_own_real_residual_snapshot(self):
        result = run_scenario("SC05")
        self.assertEqual(len(result["history"]), 13)
        for step in result["history"]:
            self.assertEqual(len(step["residual_snapshot"]), 88)
            self.assertGreater(step["bottleneck"], 0)
            flows = flow_from_residual_snapshot(result["edges"], step["residual_snapshot"])
            self.assertEqual(sum(flows[e["id"]] for e in result["edges"]
                                 if e["u"] == "SS"), step["total_flow"])
        self.assertEqual(result["history"][-1]["residual_snapshot"], result["residual_final"])

    def test_graph_layer_and_cut_explanations(self):
        result = run_scenario("SC04")
        fig = graph_figure(result["nodes"], result["edges"],
                           cut_ids=[e["edge_id"] for e in result["cut_edges"]])
        self.assertGreater(len(fig.data), 40)
        n_edges = filter_graph_edges(result["edges"], "N")
        self.assertGreater(len(n_edges), 4)
        self.assertLess(len(n_edges), 44)
        kinds = [cut_meaning(e) for e in result["cut_edges"]]
        self.assertTrue(any("Hướng thoát" in x for x in kinds))


if __name__ == "__main__":
    unittest.main()
