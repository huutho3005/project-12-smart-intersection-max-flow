"""Chạy: python -m unittest discover -s tests -v"""
import csv
import unittest
from pathlib import Path

from graph import FlowGraph
from edmonds_karp import edmonds_karp
from ford_fulkerson import ford_fulkerson_dfs
from validator import verify_max_flow, check_movement_demands, validate_scenario_metadata
from scenario import load_scenario
from min_cut import min_cut


class TestAlgorithms(unittest.TestCase):
    def build(self, vertices, edges):
        g = FlowGraph(vertices)
        for i, (u, v, c) in enumerate(edges, 1):
            g.add_edge("E%03d" % i, u, v, c)
        return g

    def check_two_methods(self, graph, expected, s="s", t="t"):
        bfs_graph = graph.clone()
        dfs_graph = graph.clone()
        flow_bfs, history_bfs = edmonds_karp(bfs_graph, s, t)
        flow_dfs, history_dfs = ford_fulkerson_dfs(dfs_graph, s, t)
        self.assertEqual(flow_bfs, expected)
        self.assertEqual(flow_dfs, expected)
        self.assertEqual(verify_max_flow(bfs_graph, flow_bfs, s, t)["cut_capacity"], expected)
        self.assertEqual(verify_max_flow(dfs_graph, flow_dfs, s, t)["cut_capacity"], expected)
        return history_bfs, history_dfs

    def test_01_disconnected(self):
        g = self.build(["s", "a", "t"], [("s", "a", 5)])
        self.check_two_methods(g, 0)

    def test_02_single_edge(self):
        g = self.build(["s", "t"], [("s", "t", 7)])
        self.check_two_methods(g, 7)

    def test_03_zero_capacity(self):
        g = self.build(["s", "a", "b", "t"],
                       [("s", "a", 0), ("a", "t", 9),
                        ("s", "b", 4), ("b", "t", 6)])
        self.check_two_methods(g, 4)

    def test_04_multiple_paths(self):
        g = self.build(["s", "a", "b", "t"],
                       [("s", "a", 3), ("a", "t", 3),
                        ("s", "b", 2), ("b", "t", 2)])
        self.check_two_methods(g, 5)

    def test_05_reverse_arc_is_needed_for_bfs(self):
        # Giữ thứ tự E003 A->C trước E004 A->D để BFS chọn đúng 2 đường.
        g = self.build(["SS", "A", "B", "C", "D", "TT"],
                       [("SS", "A", 1), ("SS", "B", 1),
                        ("A", "C", 1), ("A", "D", 1),
                        ("B", "C", 1), ("C", "TT", 1),
                        ("D", "TT", 1)])
        history_bfs, _ = self.check_two_methods(g, 2, "SS", "TT")
        self.assertEqual([x["path"] for x in history_bfs], [
            ["SS", "A", "C", "TT"],
            ["SS", "B", "C", "A", "D", "TT"]])

    def test_06_parallel_edges(self):
        g = self.build(["s", "a", "t"],
                       [("s", "a", 2), ("s", "a", 3), ("a", "t", 5)])
        self.check_two_methods(g, 5)

    def test_07_antiparallel_original_edges(self):
        # Hai cạnh gốc trái hướng cần được theo dõi riêng.
        g = self.build(["s", "a", "t"],
                       [("s", "a", 3), ("a", "s", 2), ("a", "t", 3)])
        clone = g.clone()
        flow, _ = edmonds_karp(clone, "s", "t")
        self.assertEqual(flow, 3)
        self.assertEqual(clone.original_flows()[1]["flow"], 0)
        self.assertEqual(verify_max_flow(clone, flow, "s", "t")["cut_capacity"], 3)

    def test_08_reject_bad_capacity(self):
        with self.assertRaises(ValueError):
            self.build(["s", "t"], [("s", "t", -2)])

    def test_09_source_data_all_scenarios(self):
        reference = {"SC01": 6511, "SC02": 7145, "SC03": 6073,
                     "SC04": 7708, "SC05": 7401}
        for sid, expected in reference.items():
            with self.subTest(scenario=sid):
                g, movements, lanes, info = load_scenario(sid)
                bfs_g = g.clone()
                dfs_g = g.clone()
                max_flow, history = edmonds_karp(bfs_g)
                other_flow, _ = ford_fulkerson_dfs(dfs_g)
                self.assertEqual(max_flow, expected)
                self.assertEqual(other_flow, expected)
                self.assertEqual(verify_max_flow(bfs_g, max_flow)["cut_capacity"], expected)
                self.assertEqual(sum(x["flow"] for x in check_movement_demands(bfs_g, movements)), max_flow)

    def test_10_match_reference_movement_and_cut_edges(self):
        base = Path(__file__).resolve().parents[1] / "reference"
        expected_movement = {}
        with (base / "Luong_12_Movement.csv").open(encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                expected_movement[r["scenario_id"], r["movement_id"]] = int(r["flow"])
        expected_cut = {}
        with (base / "Min_Cut.csv").open(encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                expected_cut.setdefault(r["scenario_id"], set()).add(r["edge_id"])
        for sid in ["SC01", "SC02", "SC03", "SC04", "SC05"]:
            with self.subTest(scenario=sid):
                g, movements, _, _ = load_scenario(sid)
                total, _ = edmonds_karp(g)
                outputs = check_movement_demands(g, movements)
                for item in outputs:
                    self.assertEqual(item["flow"], expected_movement[sid, item["movement_id"]])
                cut = verify_max_flow(g, total)["cut_edges"]
                self.assertEqual({edge["edge_id"] for edge in cut}, expected_cut[sid])


    def test_14_residual_snapshot_after_each_augmentation(self):
        # Do thi 6 dinh 7 canh cua muc 6.4: 2 lan tang luong.
        g = self.build(["SS", "A", "B", "C", "D", "TT"],
                       [("SS", "A", 1), ("SS", "B", 1),
                        ("A", "C", 1), ("A", "D", 1),
                        ("B", "C", 1), ("C", "TT", 1),
                        ("D", "TT", 1)])
        flow, history = edmonds_karp(g)
        self.assertEqual(flow, 2)
        self.assertEqual(len(history), 2)
        self.assertEqual(len(history[0]["residual_snapshot"]), 14)
        # Sau P1, E003 A->C het residual thuan; cung nguoc C->A = 1.
        first = history[0]["residual_snapshot"]
        arcs = {(a["edge_id"], a["arc_type"]): a["residual"] for a in first}
        self.assertEqual(arcs["E003", "forward"], 0)
        self.assertEqual(arcs["E003", "reverse"], 1)
        # P2 dung cung nguoc C->A nen sau do E003 co residual thuan = 1.
        second = history[1]["residual_snapshot"]
        arcs2 = {(a["edge_id"], a["arc_type"]): a["residual"] for a in second}
        self.assertEqual(arcs2["E003", "forward"], 1)
        self.assertEqual(arcs2["E003", "reverse"], 0)
        # Snapshot P1 phai bat bien du graph da thay doi sau P2.
        self.assertEqual(arcs["E003", "reverse"], 1)
        self.assertEqual(first[4]["residual"], 0)  # E003 forward

    def test_15_snapshot_all_scenarios_matches_final_graph(self):
        for sid in ["SC01", "SC02", "SC03", "SC04", "SC05"]:
            with self.subTest(scenario=sid):
                g, _, _, _ = load_scenario(sid)
                total, history = edmonds_karp(g)
                self.assertGreater(len(history), 0)
                for step in history:
                    self.assertEqual(len(step["residual_snapshot"]), 2 * len(g.edges))
                    self.assertGreater(step["bottleneck"], 0)
                self.assertEqual(history[-1]["residual_snapshot"], g.residual_arcs())
                self.assertEqual(history[-1]["total_flow"], total)

    def test_11_scenario_metadata_consistency(self):
        # Kiểm tra dữ liệu mô tả của cả 5 kịch bản, đặc biệt SC04/SC05.
        for sid in ["SC01", "SC02", "SC03", "SC04", "SC05"]:
            with self.subTest(scenario=sid):
                graph, movements, lanes, _ = load_scenario(sid)
                self.assertTrue(validate_scenario_metadata(graph, movements, lanes, sid))

    def test_12_detect_invalid_lane_metadata(self):
        # Mô phỏng sai thông tin LG_N_T, không sửa dữ liệu CSV gốc.
        graph, movements, lanes, _ = load_scenario("SC05")
        corrupted = [dict(x) for x in lanes]
        for lane in corrupted:
            if lane["lane_group_id"] == "LG_N_T":
                lane["assigned_movements"] = "MOV_N_T"  # thiếu rẽ phải
        with self.assertRaises(ValueError):
            validate_scenario_metadata(graph, movements, corrupted, "SC05")

    def test_13_detect_wrong_demand_limit(self):
        # SC05 dùng chung: APP_N -> LG_N_T là nút giới hạn chung.
        graph, movements, lanes, _ = load_scenario("SC05")
        wrong_graph = graph.clone()
        for edge in wrong_graph.edges:
            if edge["id"] == "E006":
                edge["capacity"] = 2000
        with self.assertRaises(ValueError):
            validate_scenario_metadata(wrong_graph, movements, lanes, "SC05")


if __name__ == "__main__":
    unittest.main()
