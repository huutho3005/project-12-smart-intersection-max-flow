"""Kiểm chứng độc lập 2 tiến trình: Python main.py và chương trình C++17 tự cài.

Lệnh: python verify_independent_processes.py
* Chạy Python thành tiến trình riêng và đọc CSV kết quả do Python tạo.
* Biên dịch C++17, chạy thành tiến trình riêng trên cùng tập CSV đầu vào.
* So sánh kết quả TỰ TÍNH từ hai chương trình. Không sử dụng giá trị chuẩn gán sẵn.
* Khi khác nhau: lưu cả hai log, ghi FAIL, thoát mã lỗi 1 (KHÔNG sửa kết quả).
"""
import csv
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
REPORT_DIR = ROOT / "outputs" / "kiem_chung_python_cpp_doc_lap"
SCENARIOS = ["SC01", "SC02", "SC03", "SC04", "SC05"]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect_version_manifest():
    """SHA-256 của toàn bộ file nguồn/dữ liệu/tài liệu có trong gói.

    Không đưa outputs, Python/pytest cache hoặc thư mục môi trường ảo vào hash.
    outputs là sản phẩm sau chạy; cache cũng chỉ là tệp tạm tạo khi kiểm thử.
    """
    tracked_extensions = {".py", ".cpp", ".csv", ".md", ".txt", ".png", ".pdf"}
    ignored_dirs = {"outputs", "__pycache__", ".pytest_cache", ".mypy_cache",
                    ".ruff_cache", ".git", ".venv", "venv", "env", "build",
                    "dist", ".tox", ".nox"}
    entries = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in tracked_extensions:
            continue
        rel = path.relative_to(ROOT)
        if any(part in ignored_dirs for part in rel.parts):
            continue
        if rel.parts[0] == "data":
            category = "data_and_scenario_metadata"
        elif rel.parts[0] == "tests":
            category = "test_code_or_fixture"
        elif rel.parts[0] == "reference":
            category = "reference_test_outputs"
        elif rel.parts[0] == "minh_chung_trinh_duyet":
            category = "browser_screenshot_evidence"
        elif path.suffix.lower() == ".py":
            category = "python_source"
        elif path.suffix.lower() == ".cpp":
            category = "cpp_source"
        else:
            category = "documentation"
        entries.append({"file": rel.as_posix(), "category": category,
                        "sha256": digest(path)})
    entries.sort(key=lambda row: row["file"])
    fingerprint = hashlib.sha256("".join(
        f'{entry["file"]}\t{entry["sha256"]}\n' for entry in entries
    ).encode("utf-8")).hexdigest()
    return entries, fingerprint


def csv_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows, fields):
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def execute(args, cwd):
    process = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    return process


def compare(py_by_id, cpp_by_id):
    """So sánh dữ liệu đầu ra, không điều chỉnh hay điền giá trị nào."""
    if set(py_by_id) != set(SCENARIOS) or set(cpp_by_id) != set(SCENARIOS):
        raise AssertionError("Thiếu/thừa scenario trong một trong hai kết quả")
    results = []
    for sid in SCENARIOS:
        a = py_by_id[sid]
        b = cpp_by_id[sid]
        py_flow = int(a["max_flow"])
        cpp_flow = int(b["max_flow"])
        py_cut = int(a["min_cut"])
        cpp_cut = int(b["min_cut"])
        delta = py_flow - cpp_flow
        status = "PASS" if (delta == 0 and py_flow == py_cut and cpp_flow == cpp_cut) else "FAIL"
        results.append({
            "scenario_id": sid,
            "python_max_flow": py_flow,
            "cpp_max_flow": cpp_flow,
            "chenh_lech_python_tru_cpp": delta,
            "python_min_cut": py_cut,
            "cpp_min_cut": cpp_cut,
            "python_bfs_iterations": int(a["bfs_iterations"]),
            "cpp_bfs_iterations": int(b["bfs_iterations"]),
            "ket_qua": status,
        })
    return results


def main():
    compiler = shutil.which("g++")
    if compiler is None:
        raise RuntimeError("Chưa cài đặt g++ (hỗ trợ C++17). Không thể xác nhận kiểm chứng độc lập.")
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    data_inputs = [ROOT / "data" / "Nodes.csv"] + [
        ROOT / "data" / "scenarios" / sid / "Edges.csv" for sid in SCENARIOS
    ]
    metadata = [{"file": str(p.relative_to(ROOT)), "sha256": digest(p)} for p in data_inputs]
    write_csv(REPORT_DIR / "SHA256_DU_LIEU_GOC.csv", metadata, ["file", "sha256"])
    # Snapshot toàn bộ phiên bản: mọi module Python và bảng CSV metadata SC01–SC05,
    # mã C++, fixture kiểm thử và tài liệu (không gồm outputs/ vì là kết quả chạy).
    tracked_files, tree_hash = collect_version_manifest()
    write_csv(REPORT_DIR / "SHA256_TOAN_BO_SOURCE_DATA.csv", tracked_files,
              ["file", "category", "sha256"])

    with tempfile.TemporaryDirectory(prefix="smart_intersection_compare_") as tmp:
        temp = Path(tmp)
        executable = temp / "ek_cpp_independent"
        compile_command = [compiler, "-std=c++17", "-O2", "-Wall", "-Wextra",
                           str(ROOT / "cpp_edmonds_karp.cpp"), "-o", str(executable)]
        built = execute(compile_command, cwd=ROOT)
        (REPORT_DIR / "CPP_COMPILE.log").write_text(
            "COMMAND: " + " ".join(compile_command) + "\n" +
            f"RETURN_CODE: {built.returncode}\n" + built.stdout + built.stderr,
            encoding="utf-8")
        if built.returncode != 0:
            raise RuntimeError("C++ biên dịch lỗi; xem CPP_COMPILE.log")

        # Process 1: Python tự tính và tạo summary.csv trong thư mục TẠM trống.
        py_cmd = [sys.executable, str(ROOT / "main.py"), "--all",
                  "--output", str(temp / "python_output")]
        py = execute(py_cmd, cwd=ROOT)
        (REPORT_DIR / "PYTHON_RUN.log").write_text(
            "COMMAND: " + " ".join(py_cmd) + "\n" +
            f"RETURN_CODE: {py.returncode}\n" + py.stdout + py.stderr,
            encoding="utf-8")
        if py.returncode != 0:
            raise RuntimeError("Python lỗi; xem PYTHON_RUN.log")
        python_csv = temp / "python_output" / "summary.csv"
        if not python_csv.is_file():
            raise RuntimeError("Python không xuất summary.csv")
        shutil.copy2(python_csv, REPORT_DIR / "PYTHON_RAW_SUMMARY.csv")

        # Process 2: executable C++ riêng tự đọc cùng data/scenarios/SCxx/Edges.csv.
        cpp_cmd = [str(executable), "--all", "--data", str(ROOT / "data")]
        cpp = execute(cpp_cmd, cwd=ROOT)
        (REPORT_DIR / "CPP_RUN.log").write_text(
            "COMMAND: " + " ".join(cpp_cmd) + "\n" +
            f"RETURN_CODE: {cpp.returncode}\n" + cpp.stdout + cpp.stderr,
            encoding="utf-8")
        if cpp.returncode != 0:
            raise RuntimeError("C++ lỗi; xem CPP_RUN.log")
        (REPORT_DIR / "CPP_RAW_SUMMARY.csv").write_text(cpp.stdout, encoding="utf-8-sig")

        py_rows = csv_rows(python_csv)
        cpp_rows = list(csv.DictReader(io.StringIO(cpp.stdout)))
        py_by_id = {row["scenario_id"]: row for row in py_rows}
        cpp_by_id = {row["scenario_id"]: row for row in cpp_rows}
        if len(py_rows) != len(py_by_id) or len(cpp_rows) != len(cpp_by_id):
            raise AssertionError("Trùng scenario ID trong output; kiểm tra dữ liệu")
        results = compare(py_by_id, cpp_by_id)
        write_csv(REPORT_DIR / "SO_SANH_PYTHON_CPP_5_KICH_BAN.csv", results, list(results[0]))

    passed = sum(row["ket_qua"] == "PASS" for row in results)
    manifest = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python_executable": sys.executable,
        "python_version": sys.version.split()[0],
        "cpp_compiler": compiler,
        "source_python_sha256": digest(ROOT / "edmonds_karp.py"),
        "source_cpp_sha256": digest(ROOT / "cpp_edmonds_karp.cpp"),
        "input_files": metadata,  # 6 file dùng chung trực tiếp để so sánh
        "all_version_files": tracked_files,
        "all_version_file_count": len(tracked_files),
        "source_data_tree_sha256": tree_hash,
        "tracked_extensions": [".py", ".cpp", ".csv", ".md", ".txt", ".png", ".pdf"],
        "excluded_generated_paths": ["outputs", "__pycache__"],
        "scenario_count": len(results),
        "passed": passed,
        "result": "PASS" if passed == len(results) else "FAIL",
    }
    (REPORT_DIR / "MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# Biên bản kiểm chứng hai chương trình độc lập", "",
             "- Python chạy `main.py` trong tiến trình riêng.",
             "- C++17 được biên dịch từ `cpp_edmonds_karp.cpp`, chạy tiến trình riêng.",
             "- Cả hai tự đọc cùng các file `Nodes.csv` và `scenarios/SCxx/Edges.csv`.",
             "- Giá trị trong bảng lấy trực tiếp từ hai đầu ra mới sinh, KHÔNG được gán cứng.",
             "- SHA256_DU_LIEU_GOC.csv lưu sáu đầu vào cốt lõi dùng chung giữa hai chương trình.",
             "- SHA256_TOAN_BO_SOURCE_DATA.csv và MANIFEST.json lưu SHA-256 mọi module .py,",
             "  mã .cpp, mọi bảng CSV dữ liệu/metadata SC01–SC05, fixture, tài liệu và reference.",
             "- Không băm thư mục outputs vì đó là kết quả chạy có thể tự thay đổi.",
             f"- Tổng file theo dõi: {len(tracked_files)}; fingerprint cây: {tree_hash}.",
             "- Sai khác sẽ ghi FAIL và chương trình trả mã lỗi; không tự sửa dữ liệu hoặc kết quả.",
             "", "| Scenario | Python | C++ | Chênh lệch | Min-Cut Python | Min-Cut C++ | Kết quả |",
             "|---|---:|---:|---:|---:|---:|---|"]
    for r in results:
        lines.append("| {scenario_id} | {python_max_flow:,} | {cpp_max_flow:,} | "
                     "{chenh_lech_python_tru_cpp:,} | {python_min_cut:,} | "
                     "{cpp_min_cut:,} | {ket_qua} |".format(**r))
    lines += ["", f"**Kết quả: {passed}/{len(results)} kịch bản đạt.**", "",
              "Giới hạn: kiểm chứng độc lập mã thuật toán và đọc dữ liệu, "
              "không kiểm chứng độ chính xác của Capacity/Demand ngoài thực địa."]
    (REPORT_DIR / "BIEN_BAN_KIEM_CHUNG.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("Scenario | Python | C++ | Chênh lệch | Python Min-Cut | C++ Min-Cut | PASS/FAIL")
    for r in results:
        print(f"{r['scenario_id']:8s} | {r['python_max_flow']:6d} | {r['cpp_max_flow']:5d} | "
              f"{r['chenh_lech_python_tru_cpp']:10d} | {r['python_min_cut']:14d} | "
              f"{r['cpp_min_cut']:11d} | {r['ket_qua']}")
    print("Output:", REPORT_DIR)
    if passed != len(results):
        raise AssertionError("Sai khác Python vs C++: cần điều tra lỗi, không chỉnh kết quả cho bằng nhau")


if __name__ == "__main__":
    main()
