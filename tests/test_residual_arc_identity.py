"""Kiểm chứng danh tính cung dư khi có hai cạnh gốc ngược chiều hoặc song song."""
import unittest
from graph import FlowGraph
from edmonds_karp import edmonds_karp
from run_edge_cases import selected_reverse_edges
from validator import verify_max_flow


class TestArcIdentity(unittest.TestCase):
    def test_antiparallel_original_still_uses_reverse_residual(self):
        # EC05, thêm cạnh gốc C->A. Khi vòng 2 đi C->A, BFS chọn
        # CUNG NGƯỢC của E003 A->C chứ KHÔNG chọn cạnh gốc E008 C->A.
        g = FlowGraph(["SS", "A", "B", "C", "D", "TT"])
        for eid, u, v in [
            ("E001", "SS", "A"), ("E002", "SS", "B"),
            ("E003", "A", "C"), ("E004", "A", "D"),
            ("E005", "B", "C"), ("E006", "C", "TT"),
            ("E007", "D", "TT"), ("E008", "C", "A")]:
            g.add_edge(eid, u, v, 1)
        flow, hist = edmonds_karp(g)
        self.assertEqual(flow, 2)
        self.assertEqual(len(hist), 2)
        self.assertEqual(hist[1]["path"], ["SS", "B", "C", "A", "D", "TT"])
        chosen = hist[1]["path_arcs"][2]
        self.assertEqual((chosen["edge_id"], chosen["arc_type"],
                          chosen["from"], chosen["to"]),
                         ("E003", "reverse", "C", "A"))
        self.assertIn("E003", selected_reverse_edges(hist[1]))
        self.assertNotIn("E008", selected_reverse_edges(hist[1]))
        self.assertEqual(next(e["flow"] for e in g.original_flows()
                              if e["edge_id"] == "E008"), 0)
        self.assertEqual(verify_max_flow(g, flow)["cut_capacity"], 2)

    def test_antiparallel_forward_not_mislabeled_reverse(self):
        g = FlowGraph(["SS", "A", "C", "TT"])
        for eid,u,v,c in [
            ("E001", "SS", "C", 1),
            ("E002", "C", "A", 1),
            ("E003", "A", "C", 1),
            ("E004", "A", "TT", 1)]:
            g.add_edge(eid, u, v, c)
        f,hist = edmonds_karp(g)
        self.assertEqual(f,1)
        self.assertEqual(hist[0]["path_arcs"][1]["edge_id"], "E002")
        self.assertEqual(hist[0]["path_arcs"][1]["arc_type"], "forward")
        self.assertEqual(selected_reverse_edges(hist[0]), [])

    def test_parallel_original_edges_keep_distinct_ids(self):
        g = FlowGraph(["SS", "A", "TT"])
        for eid, u, v, c in [
            ("E001", "SS", "A", 2),
            ("E002", "SS", "A", 3),
            ("E003", "A", "TT", 5)]:
            g.add_edge(eid, u, v, c)
        f,hist = edmonds_karp(g)
        self.assertEqual(f,5)
        self.assertEqual([h["path_arcs"][0]["edge_id"] for h in hist],
                         ["E001", "E002"])
        self.assertTrue(all(a["arc_type"] == "forward" for h in hist
                            for a in h["path_arcs"]))


if __name__ == "__main__":
    unittest.main()
