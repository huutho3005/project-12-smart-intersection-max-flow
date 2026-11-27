# SMART INTERSECTION – Đề tài 12

Bài tập lớn Cấu trúc rời rạc, Đại học Giao thông vận tải TP.HCM.

Bài toán tính lưu lượng phương tiện tối đa qua nút giao nhiều làn trong giờ cao điểm. Mô hình gồm 34 đỉnh, 44 cạnh có hướng, 12 nhóm chuyển động và 5 kịch bản. Thuật toán chính là Edmonds–Karp; Ford–Fulkerson (DFS) và C++17 được dùng để đối chiếu.

Capacity và Demand là số liệu giả định, đơn vị xe quy ước/giờ. Kết quả không thay thế khảo sát giao thông thực tế.

## Cài đặt và chạy

Cần Python và các thư viện trong `requirements.txt`. Cài thêm `g++` hỗ trợ C++17 để đối chiếu Python và C++.

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Website gồm 6 trang; trang Mô hình hỗ trợ Capacity, Flow/Capacity, Residual, Minimum Cut và so sánh kịch bản với SC02.

Chạy bằng terminal:

```bash
python main.py --scenario SC02 --history
python main.py --all
```

## Kết quả 5 kịch bản

| Kịch bản | Demand | Max-Flow | Min-Cut | Chưa phục vụ |
|---|---:|---:|---:|---:|
| SC01 – Cơ sở | 6870 | 6511 | 6511 | 359 |
| SC02 – Giờ cao điểm | 8932 | 7145 | 7145 | 1787 |
| SC03 – Suy giảm năng lực | 8932 | 6073 | 6073 | 2859 |
| SC04 – Bổ sung 2 làn quy đổi | 8932 | 7708 | 7708 | 1224 |
| SC05 – Điều chỉnh chức năng làn | 8932 | 7401 | 7401 | 1531 |

## Cấu trúc chương trình

| Tệp hoặc thư mục | Chức năng |
|---|---|
| `graph.py`, `bfs.py` | Mạng dư, tìm đường tăng |
| `edmonds_karp.py`, `ford_fulkerson.py` | Max-Flow bằng BFS và DFS |
| `min_cut.py`, `validator.py` | Lát cắt và kiểm tra luồng |
| `scenario.py`, `data/` | Đọc dữ liệu kịch bản |
| `main.py`, `app.py`, `ui_data.py`, `ui_graph.py` | Terminal và website |
| `cpp_edmonds_karp.cpp` | Thuật toán độc lập C++17 |
| `tests/`, `reference/` | Kiểm thử và dữ liệu đối chứng |
| `benchmark.py`, `verify_benchmark.py` | Đo và kiểm tra hiệu suất |
| `sensitivity_analysis.py` | Phân tích độ nhạy SC02 |
| `outputs/` | Kết quả thực nghiệm và kiểm chứng |

DFS sử dụng stack, không đệ quy. Hai thuật toán thay đổi mạng dư trực tiếp; sử dụng `graph.clone()` để chạy lại từ luồng 0. Cả hai hỗ trợ `save_history=False` khi không cần lưu lịch sử. Mỗi cặp cung dư được liên kết bằng `rev` để xử lý cung đảo và cạnh song song.

## Kiểm thử

```bash
python -m pytest -q
python run_edge_cases.py
python report_cut.py
python verify_python_cpp.py
python verify_independent_processes.py
python kiem_tra_manifest_sha256.py
```

`verify_independent_processes.py` chạy hai chương trình độc lập và tạo manifest. Chạy kiểm tra manifest trước khi tạo lại nếu muốn xác minh bộ tệp đã nộp. Cấu hình CI nằm trong `.github/workflows/tests.yml`; trạng thái thực thi xem tại tab Actions.

## Benchmark

| Đồ thị (V, E) | DFS (ms) | BFS (ms) |
|---|---:|---:|
| Small (6, 8) | 0,022291 | 0,019947 |
| SC01 (34, 44) | 0,230978 | 0,259947 |
| SC02 (34, 44) | 0,254532 | 0,289215 |
| Large (322, 440) | 8,959047 | 16,678297 |

Kết quả đo trên AMD Ryzen 5 7520U, Linux, Python 3.14.10. Có 9 đợt đo, 20 lần warm-up cho mỗi cặp đồ thị–thuật toán, tổng 54.090 mẫu. Cả hai tắt lịch sử; không tính đọc CSV, tạo hoặc sao chép đồ thị. Thống kê là trung vị của các trung vị từng đợt.

```bash
python verify_benchmark.py
python benchmark.py --output outputs/benchmark_tai_do --batches 9 --reps 1000 --large-reps 5 --warmup 20
```

Dữ liệu đo chính thức nằm trong `outputs/benchmark/`. DFS nhanh hơn trên ba đồ thị trong phép đo này, không có nghĩa DFS luôn nhanh hơn BFS. Thứ tự đo cố định và tải máy có thể ảnh hưởng kết quả.

## Phân tích độ nhạy SC02

```bash
python sensitivity_analysis.py
```

| Thay đổi | Max-Flow | Chênh lệch |
|---|---:|---:|
| SC02 gốc | 7145 | 0 |
| Nới Demand | 8208 | +1063 |
| E021 +100 | 7245 | +100 |
| E027 +100 | 7245 | +100 |
| Cả hai +100 | 7345 | +200 |
| Năng lực nhóm làn -10% | 6613 | -532 |
| Năng lực nhóm làn +10% | 7672 | +527 |

Kết quả tại `outputs/sensitivity_analysis.csv`. Các phương án dùng bản sao mạng, không sửa CSV gốc.

## Giới hạn và minh chứng

Mô hình là mạng luồng tĩnh, chưa xét đầy đủ xung đột chuyển động, chu kỳ đèn và hàng đợi. Cung dư ngược dùng để phân bổ lại luồng, không phải chiều xe chạy. Minh chứng website trong `minh_chung_trinh_duyet/`; ảnh 01–06 là ảnh trình duyệt đã có, hình 07–09 kết xuất từ source. Kiểm thử giao diện giả lập không thay thế kiểm tra trình duyệt thật.
