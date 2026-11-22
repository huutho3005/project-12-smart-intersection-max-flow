"""Kiểm lại SHA-256 theo manifest của lần chạy Python–C++ gần nhất.
Chạy: python kiem_tra_manifest_sha256.py
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "outputs" / "kiem_chung_python_cpp_doc_lap" / "MANIFEST.json"


def verify_manifest(path=MANIFEST):
    manifest = json.loads(Path(path).read_text(encoding="utf-8"))
    entries = manifest["all_version_files"]
    errors = []
    for entry in entries:
        file = ROOT / entry["file"]
        if not file.is_file():
            errors.append("THIEU: " + entry["file"])
        elif hashlib.sha256(file.read_bytes()).hexdigest() != entry["sha256"]:
            errors.append("THAY_DOI: " + entry["file"])
    old = {e["file"] for e in entries}
    from verify_independent_processes import collect_version_manifest
    current, fingerprint = collect_version_manifest()
    new = {e["file"] for e in current}
    for added in sorted(new-old):
        errors.append("THEM_MOI: " + added)
    if fingerprint != manifest["source_data_tree_sha256"]:
        errors.append("TREE_HASH_KHAC")
    print(f'Đã so sánh {len(entries)} file, phát hiện {len(errors)} vấn đề.')
    for item in errors:
        print(item)
    if errors:
        raise SystemExit(1)
    print("PASS: manifest khớp hoàn toàn với phiên bản đang có")


if __name__ == "__main__":
    verify_manifest()
