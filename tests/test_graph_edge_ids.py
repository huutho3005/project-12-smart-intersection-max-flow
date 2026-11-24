"""Kiểm tra đăng ký edge_id bằng set, tính nhất quán khi sao chép mạng."""
import unittest
from graph import FlowGraph


class TestGraphEdgeIds(unittest.TestCase):
    def test_duplicate_edge_id_rejected_without_mutating_graph(self):
        g = FlowGraph(["SS", "A", "TT"])
        g.add_edge("e01", "SS", "A", 4)
        with self.assertRaisesRegex(ValueError, "Trùng mã cạnh"):
            g.add_edge("e01", "A", "TT", 3)
        self.assertEqual(len(g.edges), 1)
        self.assertEqual(len(g.residual_arcs()), 2)
        self.assertEqual(g.edge_ids, {"e01"})

    def test_invalid_edge_does_not_reserve_id(self):
        g = FlowGraph(["SS", "TT"])
        with self.assertRaisesRegex(ValueError, "Capacity không hợp lệ"):
            g.add_edge("e01", "SS", "TT", -1)
        self.assertNotIn("e01", g.edge_ids)
        g.add_edge("e01", "SS", "TT", 2)
        self.assertEqual(len(g.edges), 1)

    def test_parallel_and_opposing_edges_keep_separate_ids(self):
        g = FlowGraph(["SS", "A", "TT"])
        g.add_edge("e01", "SS", "A", 5)
        g.add_edge("e02", "SS", "A", 6)
        g.add_edge("e03", "A", "SS", 3)
        self.assertEqual(g.edge_ids, {"e01", "e02", "e03"})
        self.assertEqual(len(g.residual_arcs()), 6)

    def test_clone_rebuilds_edge_id_set(self):
        g = FlowGraph(["SS", "TT"])
        g.add_edge("e01", "SS", "TT", 1)
        copied = g.clone()
        self.assertEqual(copied.edge_ids, {"e01"})
        with self.assertRaisesRegex(ValueError, "Trùng mã cạnh"):
            copied.add_edge("e01", "SS", "TT", 2)
        copied.add_edge("e02", "SS", "TT", 2)
        self.assertEqual(g.edge_ids, {"e01"})
        self.assertEqual(copied.edge_ids, {"e01", "e02"})


if __name__ == "__main__":
    unittest.main()
