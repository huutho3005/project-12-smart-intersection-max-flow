"""Kiểm thử giao diện ở lớp tính toán; KHÔNG thay cho chạy trình duyệt Streamlit."""
import unittest
from ui_data import run_all, run_scenario, cut_meaning, scenario_edge_changes
from ui_graph import graph_figure, residual_figure, flow_from_residual_snapshot, filter_graph_edges


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


    def test_scenario_edge_changes_identifies_capacity_and_connection_changes(self):
        baseline = run_scenario("SC02")
        sc04 = run_scenario("SC04")
        sc05 = run_scenario("SC05")
        changes04 = scenario_edge_changes(baseline["edges"], sc04["edges"])
        changes05 = scenario_edge_changes(baseline["edges"], sc05["edges"])
        self.assertEqual(changes04["E021"]["status"], "increased")
        self.assertEqual(changes04["E027"]["status"], "increased")
        self.assertEqual(changes05["E007"]["status"], "inactive")
        self.assertEqual(changes05["E019"]["status"], "connection_changed")
        self.assertEqual(changes05["E006"]["status"], "increased")

    def test_replay_highlight_overrides_capacity_and_flow_colors(self):
        result = run_scenario("SC02")
        first = result["history"][0]
        path_ids = {a["edge_id"] for a in first["path_arcs"]}
        flows = flow_from_residual_snapshot(result["edges"], first["residual_snapshot"])
        for mode in ("Capacity", "Flow/Capacity"):
            with self.subTest(mode=mode):
                fig = graph_figure(result["nodes"], result["edges"],
                                   mode=mode, path_ids=path_ids, flows=flows)
                actual = {e["id"] for i, e in enumerate(result["edges"])
                          if fig.data[i].line.color == "#eb9634"}
                self.assertEqual(actual, path_ids)

    def test_replay_rejects_wrong_residual_arc_orientation(self):
        result = run_scenario("SC05")
        arcs = [dict(a) for a in result["history"][12]["path_arcs"]]
        i = next(i for i, a in enumerate(arcs) if a["edge_id"] == "E030")
        arcs[i]["from"], arcs[i]["to"] = arcs[i]["to"], arcs[i]["from"]
        with self.assertRaisesRegex(ValueError, "Chiều cung dư"):
            graph_figure(result["nodes"], result["edges"], path_arcs=arcs)

    def test_min_cut_mode_ignores_unrelated_highlight_ids(self):
        result = run_scenario("SC05")
        cut_ids = {e["edge_id"] for e in result["cut_edges"]}
        fig = graph_figure(result["nodes"], result["edges"],
                           mode="Minimum Cut", cut_ids=cut_ids,
                           path_ids={"E001", "E002"})
        red = {e["id"] for i, e in enumerate(result["edges"])
               if fig.data[i].line.color == "#d64141"}
        orange = {e["id"] for i, e in enumerate(result["edges"])
                  if fig.data[i].line.color == "#eb9634"}
        self.assertEqual(red, cut_ids)
        self.assertEqual(orange, set())

    def test_four_visualization_modes_have_real_graph_data(self):
        result = run_scenario("SC05")
        baseline = run_scenario("SC02")
        changes = scenario_edge_changes(baseline["edges"], result["edges"])
        flows = {e["edge_id"]: e["flow"] for e in result["edge_flows"]}
        capacity_fig = graph_figure(result["nodes"], result["edges"], mode="Capacity",
                                    edge_states=changes)
        flow_fig = graph_figure(result["nodes"], result["edges"], mode="Flow/Capacity",
                                flows=flows)
        cut_fig = graph_figure(result["nodes"], result["edges"], mode="Minimum Cut",
                               cut_ids=[e["edge_id"] for e in result["cut_edges"]])
        residual_fig = residual_figure(result["nodes"], result["edges"],
                                       result["residual_final"])
        for fig in (capacity_fig, flow_fig, cut_fig, residual_fig):
            self.assertGreater(len(fig.data), 30)

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
