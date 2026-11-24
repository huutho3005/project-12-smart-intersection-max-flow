"""Kiểm chứng độc lập từ benchmark_raw.csv, summary.csv và metadata.json.
Chạy: python verify_benchmark.py  (từ thư mục gốc SMART INTERSECTION)
Không đo thời gian lại: chỉ xác thực dữ liệu, giao thức đo và mã nguồn.
"""
import csv
import hashlib
import json
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIR = ROOT / "outputs" / "benchmark"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    with (DIR / "benchmark_raw.csv").open(newline="", encoding="utf-8") as f:
        raw = list(csv.DictReader(f))
    with (DIR / "benchmark_summary.csv").open(newline="", encoding="utf-8") as f:
        summary = list(csv.DictReader(f))
    metadata = json.loads((DIR / "benchmark_metadata.json").read_text(encoding="utf-8"))
    batches = int(metadata["args"]["batches"])
    assert batches == 9, "Giao thức benchmark khác 9 đợt"
    buckets = defaultdict(list)
    for item in raw:
        k = (item["graph"], item["algorithm"], int(item["batch"]))
        buckets[k].append((int(item["repetition"]), float(item["algorithm_time_ms"])))
    assert len(summary) == 8, "Phải có 8 kết quả: 4 đồ thị x 2 thuật toán"
    assert len(raw) == 54090, "Số lượng mẫu thô khác 54.090"
    seen = set()
    for r in summary:
        key = (r["graph"], r["algorithm"])
        assert key not in seen, "Có dữ liệu tổng hợp trùng"
        seen.add(key)
        count = int(r["reps_per_batch"])
        assert count == (5 if r["graph"].startswith("Large-") else 1000)
        assert int(r["batches"]) == 9 and int(r["warmup"]) == 20
        medians = []
        for b in range(1, batches + 1):
            values = buckets[key + (b,)]
            assert len(values) == count, f"Thiếu mẫu cho {key}, đợt {b}"
            assert sorted(i for i, _ in values) == list(range(1, count + 1))
            medians.append(statistics.median(t for _, t in values))
        actual = round(statistics.median(medians), 6)
        published = float(r["median_of_batch_medians_ms"])
        assert abs(actual - published) < 0.00000051, (key, actual, published)
        print(f"PASS {key[0]:18s} {key[1]:3s}: {actual:.6f} ms")
    for file, expected in metadata.get("source_sha256", {}).items():
        actual = sha256(ROOT / file)
        assert actual == expected, f"Mã nguồn {file} khác bản được benchmark"
    print(f"PASS: {len(raw):,} mẫu thô, {len(summary)}/8 trung vị,"
          f" {len(metadata.get('source_sha256', {}))} mã nguồn khớp SHA-256")


if __name__ == "__main__":
    verify()
