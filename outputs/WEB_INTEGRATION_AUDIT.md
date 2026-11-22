# Bước 14 – Kiểm tra tích hợp SMART INTERSECTION 6 trang

- Nguồn: gói Python 8 module + C++ độc lập đã kiểm chứng ở bước trước, không sửa thuật toán gốc.
- 6 mục điều hướng Streamlit: Tổng quan, Mô hình, Chọn Scenario, Edmonds–Karp, Minimum Cut, So sánh.
- Lớp cầu nối: `ui_data.py` thực sự gọi `load_scenario()`, `edmonds_karp()`, `ford_fulkerson_dfs()`, `verify_max_flow()`, `check_movement_demands()`.
- Đồ thị: 34 Nodes, 44 Edges, 44 mũi tên có hướng, lọc theo hướng, hover Capacity/Flow.
- Lịch sử thuật toán: 12,12,12,12,13 lần tăng cho SC01–SC05; 88 cung dư/snapshot.
- Kết quả Max-Flow/Min-Cut SC01–SC05: 6511; 7145; 6073; 7708; 7401.
- Kiểm thử: 29/29 unit tests PASS, bao gồm 3 bài kiểm thử mới về kết nối website.
- So sánh hai tiến trình Python/C++: 5/5 PASS; chênh lệch 0; SHA manifest mới khớp.
- Kiểm thử smoke 6 nhánh điều hướng với API Streamlit **giả lập**: đều đi qua không lỗi (không phải kiểm thử trình duyệt).

**Hạn chế kiểm thử:** Không có thư viện `streamlit` trong môi trường này, lệnh cài gói bị lỗi kết nối mạng. Chưa thể thực thi UI trình duyệt thật tại đây; cần kiểm tra tương tác sau khi cài trên máy người dùng bằng `streamlit run app.py`.
