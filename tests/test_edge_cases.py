"""7 bài Edge Cases theo Chương 6.5 và ví dụ Capacity=0 bổ sung.
Chạy: python -m unittest discover -s tests -v
"""
import unittest
from edge_cases import read_cases, load_case
from edmonds_karp import edmonds_karp
from ford_fulkerson import ford_fulkerson_dfs
from validator import verify_max_flow

CASES={case["case_id"]:case for case in read_cases()}

class TestEdgeCases(unittest.TestCase):
    def check_case(self, case_id):
        graph=load_case(case_id)
        graph_bfs=graph.clone()
        graph_dfs=graph.clone()
        f_bfs, trace_bfs=edmonds_karp(graph_bfs)
        f_dfs, trace_dfs=ford_fulkerson_dfs(graph_dfs)
        expected=int(CASES[case_id]["expected_max_flow"])
        self.assertEqual(f_bfs,expected)
        self.assertEqual(f_dfs,expected)
        self.assertEqual(verify_max_flow(graph_bfs,f_bfs)["cut_capacity"],expected)
        self.assertEqual(verify_max_flow(graph_dfs,f_dfs)["cut_capacity"],expected)
        self.assertEqual(trace_bfs[-1]["total_flow"] if trace_bfs else 0,f_bfs)
        return graph_bfs,trace_bfs

    def test_ec01_disconnected(self):
        g,history=self.check_case("EC01")
        self.assertEqual(len(history),0)

    def test_ec02_direct_edge_capacity_7(self):
        g,history=self.check_case("EC02")
        self.assertEqual(len(history),1)
        self.assertEqual(history[0]["bottleneck"],7)

    def test_ec03a_capacity_zero_only_path(self):
        g,history=self.check_case("EC03_A")
        self.assertEqual(len(history),0)

    def test_ec03b_capacity_zero_with_alternative_path_chapter_6(self):
        g,history=self.check_case("EC03_B")
        self.assertEqual([h["path"] for h in history],[["SS","B","TT"]])

    def test_ec04_multiple_augmentations(self):
        g,history=self.check_case("EC04")
        self.assertEqual(len(history),2)
        self.assertEqual([h["bottleneck"] for h in history],[3,2])
        self.assertEqual([h["total_flow"] for h in history],[3,5])

    def test_ec05_reverse_arc_cancels_flow(self):
        g,history=self.check_case("EC05")
        self.assertEqual([h["path"] for h in history],
          [["SS","A","C","TT"],["SS","B","C","A","D","TT"]])
        def r(step,kind):
            return next(x["residual"] for x in step["residual_snapshot"]
                        if x["edge_id"]=="E003" and x["arc_type"]==kind)
        self.assertEqual((r(history[0],"forward"),r(history[0],"reverse")),(0,1))
        self.assertEqual((r(history[1],"forward"),r(history[1],"reverse")),(1,0))
        self.assertEqual(next(x["flow"] for x in g.original_flows() if x["edge_id"]=="E003"),0)
        self.assertEqual(next(x["flow"] for x in g.original_flows() if x["edge_id"]=="E004"),1)

    def test_ec06_super_source_super_sink(self):
        g,history=self.check_case("EC06")
        self.assertEqual(sum(x["flow"] for x in g.original_flows() if x["from"]=="SS"),7)

if __name__=="__main__":unittest.main()
