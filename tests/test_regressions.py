"""Kiểm thử hồi quy các lỗi đã được khắc phục."""

import unittest

from graph import FlowGraph
from scenario import load_scenario
from edmonds_karp import edmonds_karp
from ford_fulkerson import ford_fulkerson_dfs

from validator import (
    validate_scenario_metadata,
    check_residual_invariant,
    verify_max_flow
)


class TestRegressions(unittest.TestCase):

    def test_wrong_approach_is_rejected(self):
        """TC01: Phát hiện kết nối sai hướng giao thông."""

        graph, movements, lanes, _ = load_scenario("SC02")

        bad = FlowGraph(graph.nodes)

        for e in graph.edges:
            u = e["u"]

            # Cố ý đổi hướng Bắc thành hướng Nam.
            if e["id"] == "E005":
                u = "APP_S"

            bad.add_edge(
                e["id"],
                u,
                e["v"],
                e["capacity"]
            )

        with self.assertRaisesRegex(
            ValueError, "Sai hướng tiếp cận"
        ):
            validate_scenario_metadata(
                bad, movements, lanes, "SC02"
            )

    def test_residual_invariant(self):
        """TC02: Phát hiện bất biến mạng dư bị vi phạm."""

        g = FlowGraph(["s", "t"])
        g.add_edge("E01", "s", "t", 7)

        flow, _ = edmonds_karp(g, "s", "t")

        self.assertEqual(flow, 7)
        self.assertTrue(check_residual_invariant(g))

        # Lấy đúng cặp cung dư của cạnh E01.
        edge = g.edges[0]
        forward = g.adj["s"][edge["index"]]
        reverse = g.adj["t"][forward["rev"]]

        # Cố ý phá bất biến mạng dư.
        reverse["res"] = 0

        with self.assertRaisesRegex(
            AssertionError, "Vi phạm bất biến mạng dư"
        ):
            verify_max_flow(g, flow, "s", "t")

    def test_edmonds_karp_rejects_used_graph(self):
        """TC03: Edmonds-Karp từ chối đồ thị đã có luồng."""

        g = FlowGraph(["s", "t"])
        g.add_edge("E01", "s", "t", 7)

        flow, _ = edmonds_karp(g, "s", "t")
        self.assertEqual(flow, 7)

        with self.assertRaisesRegex(
            ValueError, "Đồ thị đã có luồng"
        ):
            edmonds_karp(g, "s", "t")

        # Clone phải tạo mạng dư mới.
        new_graph = g.clone()
        flow, _ = edmonds_karp(new_graph, "s", "t")
        self.assertEqual(flow, 7)

    def test_dfs_rejects_used_graph(self):
        """TC04: Ford-Fulkerson từ chối đồ thị đã có luồng."""

        g = FlowGraph(["s", "t"])
        g.add_edge("E01", "s", "t", 7)

        flow, _ = ford_fulkerson_dfs(g, "s", "t")
        self.assertEqual(flow, 7)

        with self.assertRaisesRegex(
            ValueError, "Đồ thị đã có luồng"
        ):
            ford_fulkerson_dfs(g, "s", "t")

        # Clone phải tạo mạng dư mới.
        new_graph = g.clone()
        flow, _ = ford_fulkerson_dfs(new_graph, "s", "t")
        self.assertEqual(flow, 7)

def test_dfs_long_path():
    from ford_fulkerson import dfs_path

    nodes = ["s"] + [
        "v" + str(i) for i in range(1200)
    ] + ["t"]

    g = FlowGraph(nodes)

    for i in range(len(nodes) - 1):
        g.add_edge(
            "E" + str(i),
            nodes[i],
            nodes[i + 1],
            1
        )

    path = dfs_path(g, "s", "t")
    assert len(path) == 1201

    flow, _ = ford_fulkerson_dfs(g, "s", "t")
    assert flow == 1

    assert verify_max_flow(g, flow, "s", "t")["valid"]



if __name__ == "__main__":
    unittest.main()
def test_bfs_without_history():
    """BFS tắt lịch sử không làm thay đổi kết quả."""

    base, _, _, _ = load_scenario("SC02")

    g1 = base.clone()
    g2 = base.clone()

    f1, h1 = edmonds_karp(g1, save_history=True)
    f2, h2 = edmonds_karp(g2, save_history=False)

    assert f1 == f2 == 7145
    assert len(h1) == 12
    assert h2 == []

    assert g1.residual_arcs() == g2.residual_arcs()
    assert verify_max_flow(g2, f2)["valid"]


def test_dfs_without_history():
    """DFS tắt lịch sử không làm thay đổi kết quả."""

    base, _, _, _ = load_scenario("SC02")

    g1 = base.clone()
    g2 = base.clone()

    f1, h1 = ford_fulkerson_dfs(g1, save_history=True)
    f2, h2 = ford_fulkerson_dfs(g2, save_history=False)

    assert f1 == f2 == 7145
    assert len(h1) == 12
    assert h2 == []

    assert g1.residual_arcs() == g2.residual_arcs()
    assert verify_max_flow(g2, f2)["valid"]



