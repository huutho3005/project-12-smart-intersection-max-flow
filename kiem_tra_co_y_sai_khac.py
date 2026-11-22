"""Negative test: chứng minh bộ so sánh PHÁT HIỆN chênh lệch.
Không sửa CSV, không can thiệp kết quả chạy thật. Chỉ tạo 2 kết quả GIẢ LẬP
để kiểm tra chức năng cảnh báo, tuyệt đối không dùng trong bảng báo cáo.
Không phải phép thử thay đổi CSV hay hai tiến trình đầu-cuối.
Xem thêm kiem_tra_csv_thay_doi_thuc_te.py để thử dữ liệu sửa trên bản sao.
"""
from verify_independent_processes import compare

ids = ["SC01", "SC02", "SC03", "SC04", "SC05"]
python_output = {sid: {"max_flow": "100", "min_cut": "100", "bfs_iterations": "1"}
                 for sid in ids}
cpp_output = {sid: {"max_flow": "100", "min_cut": "100", "bfs_iterations": "1"}
              for sid in ids}
cpp_output["SC03"]["max_flow"] = "99"  # Tạo sai khác giả lập để kiểm tra bộ so sánh
rows = compare(python_output, cpp_output)
assert sum(r["ket_qua"] == "FAIL" for r in rows) == 1
assert rows[2]["ket_qua"] == "FAIL"
assert rows[2]["chenh_lech_python_tru_cpp"] == 1
print("PASS: Bộ so sánh phát hiện chênh lệch cố ý ở SC03 (100 != 99), không sửa kết quả")
