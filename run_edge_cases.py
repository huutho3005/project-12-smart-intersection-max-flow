"""Chay 7 Edge Cases, ghi log chi tiet cho phu luc va van dap.
Chay: python run_edge_cases.py
"""
import csv
from pathlib import Path
from edge_cases import read_cases, load_case
from edmonds_karp import edmonds_karp
from ford_fulkerson import ford_fulkerson_dfs
from validator import verify_max_flow

OUTPUT = Path(__file__).resolve().parent / "outputs" / "edge_cases"

def write_csv(name, rows, fieldnames):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with (OUTPUT / name).open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def selected_reverse_edges(history_step):
    """Danh sách ID cạnh gốc bị hủy theo cung dư ngược thực sự được BFS chọn."""
    return [arc["edge_id"] for arc in history_step["path_arcs"]
            if arc["arc_type"] == "reverse"]


def analyze(case):
    case_id = case["case_id"]
    base = load_case(case_id)
    bfs_g, dfs_g = base.clone(), base.clone()  # hai mang du rieng
    bfs_flow, bfs_hist = edmonds_karp(bfs_g)
    dfs_flow, dfs_hist = ford_fulkerson_dfs(dfs_g)
    bfs_check = verify_max_flow(bfs_g, bfs_flow)
    dfs_check = verify_max_flow(dfs_g, dfs_flow)
    expected = int(case["expected_max_flow"])
    if not (bfs_flow == dfs_flow == bfs_check["cut_capacity"]
            == dfs_check["cut_capacity"] == expected):
        raise AssertionError(case_id + ": BFS/DFS/MinCut sai")

    reverse_used = False
    paths = []
    for h in bfs_hist:
        path = h["path"]
        selected_arcs = h["path_arcs"]
        # Mỗi phần tử đến từ đúng (u, index) mà BFS ghi vào parent.
        # Không suy luận cạnh ngược từ cặp tên đỉnh (sẽ sai với cạnh đối hướng).
        reverse_edge_ids = selected_reverse_edges(h)
        if reverse_edge_ids:
            reverse_used = True
        arc_trace = "; ".join(
            f'{arc["edge_id"]}:{arc["arc_type"]}:'
            f'{arc["from"]}->{arc["to"]}@{arc["arc_index"]}'
            for arc in selected_arcs)
        paths.append({"case_id": case_id, "iteration": h["iteration"],
                      "augmenting_path": " -> ".join(path),
                      "bottleneck": h["bottleneck"],
                      "cumulative_flow": h["total_flow"],
                      "reverse_original_edge_ids": ";".join(reverse_edge_ids),
                      "selected_residual_arcs": arc_trace})

    if case_id == "EC05":
        if [h["path"] for h in bfs_hist] != [
            ["SS", "A", "C", "TT"],
            ["SS", "B", "C", "A", "D", "TT"]]:
            raise AssertionError("EC05: thu tu BFS khong dung nhu Chuong 6.4")
        if not reverse_used or len(bfs_hist) != 2:
            raise AssertionError("EC05: khong dung cung du nguoc C->A")
        arc_1 = {(x["edge_id"],x["arc_type"]): x["residual"]
                 for x in bfs_hist[0]["residual_snapshot"]}
        arc_2 = {(x["edge_id"],x["arc_type"]): x["residual"]
                 for x in bfs_hist[1]["residual_snapshot"]}
        if (arc_1["E003","forward"],arc_1["E003","reverse"],
            arc_2["E003","forward"],arc_2["E003","reverse"]) != (0,1,1,0):
            raise AssertionError("EC05: sai cap nhat du thuan/nguoc E003")
        flow_e003 = next(x["flow"] for x in bfs_g.original_flows() if x["edge_id"]=="E003")
        if flow_e003 != 0:
            raise AssertionError("EC05: canh A->C chua bi huy luong")

    return ({"case_id":case_id,"chapter_section":case["chapter_section"],
             "description":case["description"],"vertices":len(base.nodes),
             "original_edges":len(base.edges),"expected":expected,
             "max_flow_bfs":bfs_flow,"max_flow_dfs":dfs_flow,
             "minimum_cut":bfs_check["cut_capacity"],
             "bfs_augmentations":len(bfs_hist),"dfs_augmentations":len(dfs_hist),
             "reverse_used_by_bfs":int(reverse_used),
             "cut_edges":";".join(x["edge_id"] for x in bfs_check["cut_edges"]),
             "set_S":";".join(sorted(bfs_check["S"])),
             "set_T":";".join(sorted(bfs_check["T"])),
             "result":"PASS"}, paths, bfs_hist)

def run_all():
    summary=[]; paths=[]; snapshots=[]
    for case in read_cases():
        s,p,h = analyze(case)
        summary.append(s); paths.extend(p)
        if s["case_id"]=="EC05":
            for step in h:
                for arc in step["residual_snapshot"]:
                    snapshots.append({"case_id":"EC05","iteration":step["iteration"],
                                      "edge_id":arc["edge_id"],"arc_type":arc["arc_type"],
                                      "from":arc["from"],"to":arc["to"],
                                      "residual":arc["residual"]})
    write_csv("Ket_Qua_Edge_Cases.csv",summary,list(summary[0]))
    write_csv("Lich_Su_Duong_Tang.csv",paths,list(paths[0]))
    write_csv("Residual_Tung_Vong_EC05.csv",snapshots,list(snapshots[0]))
    report = ["# KẾT QUẢ KIỂM THỬ EDGE CASES – CHƯƠNG 6.5", "",
              "Dữ liệu được đọc từ CSV fixtures; các giá trị chuẩn chỉ dùng để kiểm tra.", "",
              "| Test | Số đỉnh | Số cạnh | Kỳ vọng | BFS | DFS | Min-Cut | BFS vòng | Trạng thái |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    for s in summary:
        report.append(f'| {s["case_id"]} | {s["vertices"]} | {s["original_edges"]} | {s["expected"]} | {s["max_flow_bfs"]} | {s["max_flow_dfs"]} | {s["minimum_cut"]} | {s["bfs_augmentations"]} | {s["result"]} |')
    report += ["", "## Chứng minh cạnh dư ngược tại EC05", ""]
    for p in paths:
        if p["case_id"]=="EC05":
            report.append(f'- Vòng {p["iteration"]}: {p["augmenting_path"]}, Δ={p["bottleneck"]}, tổng F={p["cumulative_flow"]}; cạnh ngược gốc: {p["reverse_original_edge_ids"] or "không"}')
    report += ["", "Sau vòng 1, E003 A->C có dư thuận = 0, dư ngược C->A = 1.",
               "Sau vòng 2, E003 A->C có dư thuận = 1, dư ngược C->A = 0; Flow(E003)=0.",
               "", "EC03_A (F=0) là bài đơn giản hóa theo yêu cầu người dùng; EC03_B (F=4) là bài đúng mục 6.5.3 của bản nháp.",
               "", "Mọi trường hợp đã kiểm tra Capacity Constraint, Flow Conservation, BFS không còn đường tăng và Maximum Flow = Minimum Cut."]
    (OUTPUT / "BAO_CAO_EDGE_CASES.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    for s in summary:
        print(f'{s["case_id"]}: BFS={s["max_flow_bfs"]} DFS={s["max_flow_dfs"]} MinCut={s["minimum_cut"]} BFS_vong={s["bfs_augmentations"]} {s["result"]}')
    print('PASS:',len(summary),'/',len(summary),'Edge Cases')
    return summary

if __name__ == "__main__":
    run_all()
