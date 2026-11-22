"""Kiểm chứng CHÉO với C++ độc lập: python verify_python_cpp.py

Biên dịch một chương trình C++17 KHÁC cài đặt Python, tự đọc cùng CSV.
Ghi minh chứng vào outputs/python_cpp_comparison.csv.
Yêu cầu g++ có sẵn trong PATH (Linux Fedora hoặc tương thích).
"""
import csv
import io
import shutil
import subprocess
import tempfile
from pathlib import Path

from edmonds_karp import edmonds_karp
from scenario import load_scenario
from validator import verify_max_flow

ROOT = Path(__file__).resolve().parent
IDS = ["SC01", "SC02", "SC03", "SC04", "SC05"]


def main():
    compiler = shutil.which("g++")
    if compiler is None:
        raise RuntimeError("Thiếu g++; cần cài trình biên dịch C++17 để kiểm chứng độc lập")

    with tempfile.TemporaryDirectory(prefix="ctrr_cpp_") as folder:
        executable = Path(folder) / "edmonds_karp_cpp"
        subprocess.run([compiler, "-std=c++17", "-O2", "-Wall", "-Wextra",
                        str(ROOT / "cpp_edmonds_karp.cpp"), "-o", str(executable)],
                       check=True, cwd=ROOT)
        result = subprocess.run([str(executable), "--all", "--data", str(ROOT / "data")],
                                check=True, capture_output=True, text=True, cwd=ROOT)
    cpp_rows = {x["scenario_id"]: x for x in csv.DictReader(io.StringIO(result.stdout))}
    if set(cpp_rows) != set(IDS):
        raise AssertionError("C++ thiếu kịch bản hoặc xuất dữ liệu sai")

    comparison = []
    for sid in IDS:
        graph, _, _, _ = load_scenario(sid)
        py_flow, history = edmonds_karp(graph)
        py_cut = verify_max_flow(graph, py_flow)["cut_capacity"]
        cpp_flow, cpp_cut = int(cpp_rows[sid]["max_flow"]), int(cpp_rows[sid]["min_cut"])
        correct = py_flow == cpp_flow == py_cut == cpp_cut
        comparison.append({"scenario_id": sid,
                           "python_max_flow": py_flow, "cpp_max_flow": cpp_flow,
                           "python_min_cut": py_cut, "cpp_min_cut": cpp_cut,
                           "python_bfs_iterations": len(history),
                           "cpp_bfs_iterations": int(cpp_rows[sid]["bfs_iterations"]),
                           "result": "PASS" if correct else "FAIL"})
    output = ROOT / "outputs" / "python_cpp_comparison.csv"
    output.parent.mkdir(exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(comparison[0]))
        writer.writeheader()
        writer.writerows(comparison)

    for row in comparison:
        print("{scenario_id}: Python={python_max_flow}, C++={cpp_max_flow}, "
              "MinCut(Python/C++)={python_min_cut}/{cpp_min_cut}: {result}".format(**row))
    if not all(row["result"] == "PASS" for row in comparison):
        raise AssertionError("Kết quả Python và C++ không khớp")
    print("PASS 5/5, log:", output)


if __name__ == "__main__":
    main()
