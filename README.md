# SMART INTERSECTION – Đề tài 12 · Cấu trúc rời rạc

**Bản nộp:** mô hình mạng luồng 34 đỉnh, 44 cạnh gốc, 12 movement, 5 kịch bản SC01–SC05. Thuật toán chính là Edmonds–Karp (BFS), đối chiếu Ford–Fulkerson DFS và bản C++17 riêng. Website Streamlit có 6 màn hình.

> Capacity và Demand trong bộ dữ liệu là **giả định mô phỏng**, không phải số liệu khảo sát thực địa. Website phục vụ minh họa, không điều khiển giao thông.

## 1. Chuẩn bị môi trường

Cần Python 3.9 trở lên; muốn kiểm chứng C++ cần `g++` hỗ trợ C++17. Trong Terminal, mở thư mục được giải nén:

```bash
cd SMART_INTERSECTION_SOURCE_ON_DINH_DE_NOP
python -m pip install -r requirements.txt
```

**Phải cài từ `requirements.txt` trước khi chạy test và website.** File này giới hạn `pandas>=2.0,<3`, `plotly>=5.18,<7`, `streamlit>=1.32,<2`, `pytest>=8,<10`; tránh tự nâng Pandas/Plotly vượt giới hạn đã kiểm tra.

## 2. Chạy website 6 màn hình

```bash
streamlit run app.py
```

Mở địa chỉ in trong Terminal (thường là `http://localhost:8501`), kiểm tra theo thứ tự: **Tổng quan → Mô hình → Chọn Scenario → Edmonds–Karp → Minimum Cut → So sánh**. Riêng SC05, xem E007 được ghi **Nhóm làn không hoạt động (SC05)** và bảng hai cột tập S/T. Hướng dẫn chi tiết: [HUONG_DAN_WEBSITE.md](HUONG_DAN_WEBSITE.md).

`streamlit run app.py` là lệnh **mở giao diện**. `python main.py --all` chỉ chạy thuật toán bằng **dòng lệnh**.

## 3. Chạy thuật toán và các phép kiểm chứng

```bash
python main.py --scenario SC02 --history
python main.py --all
python -m pytest -q
python kiem_tra_manifest_sha256.py
python verify_independent_processes.py
```

- Bản này có **39 bài test pytest** (`39 passed`; pytest còn thông báo các subtest). Smoke test của Streamlit dùng **giao diện giả lập**, không thay cho kiểm tra trình duyệt thật.
- `verify_independent_processes.py` biên dịch và chạy C++ trong tiến trình riêng, đối chiếu kết quả mới của Python/C++ cho SC01–SC05; **5/5 kịch bản khớp**.
- Sau khi chạy `pytest`, thư mục `.pytest_cache`, `__pycache__` có thể xuất hiện; chúng được **bỏ qua trong SHA-256**. Vẫn nên xóa cache trước khi đóng ZIP nộp.
- Không tự tạo lại manifest để che giấu sai khác; chỉ tạo lại khi chính thức thay đổi source/dữ liệu/tài liệu và kiểm chứng lại.

## 4. Tóm tắt kết quả chuẩn

| Kịch bản | Demand | Maximum Flow | Minimum Cut |
|---|---:|---:|---:|
| SC01 – Cơ sở | 6.870 | 6.511 | 6.511 |
| SC02 – Giờ cao điểm | 8.932 | 7.145 | 7.145 |
| SC03 – Suy giảm | 8.932 | 6.073 | 6.073 |
| SC04 – Bổ sung 2 làn quy đổi | 8.932 | 7.708 | 7.708 |
| SC05 – Điều chỉnh chức năng làn | 8.932 | 7.401 | 7.401 |

Đơn vị: **xe quy ước/giờ**, trên mô hình giả định. Không gán cứng Max-Flow vào thuật toán.

## 5. Cấu trúc cần biết

| Thành phần | Nội dung |
|---|---|
| `graph.py`, `bfs.py` | Danh sách kề, cung dư thuận/ngược và tìm đường bằng BFS |
| `edmonds_karp.py`, `ford_fulkerson.py` | Tăng luồng BFS và DFS, lịch sử đường tăng |
| `min_cut.py`, `validator.py` | Lát cắt và kiểm tra Capacity/Flow Conservation |
| `scenario.py`, `main.py` | Đọc CSV, chạy SC01–SC05, xuất `outputs/` |
| `app.py`, `ui_data.py`, `ui_graph.py` | Website Streamlit 6 màn hình |
| `cpp_edmonds_karp.cpp` | Thuật toán kiểm chứng C++17 độc lập |
| `data/scenarios/SCxx/` | Edges, Lane_Groups và Movements theo kịch bản |
| `tests/` | 39 bài kiểm thử tự động (gồm smoke test giả lập) |
| `minh_chung_trinh_duyet/` | **Ảnh do thành viên nhóm gửi từ trình duyệt thật**, phụ lục ảnh dạng PDF |

## 6. Chứng cứ & giới hạn

Ảnh trong `minh_chung_trinh_duyet/` được **lấy từ những ảnh chụp bạn đã cung cấp**, không phải ảnh mới được tạo bằng trình duyệt trong môi trường này. Cần **chụp lại trang Minimum Cut trên bản source đã sửa E007** để chứng minh nhãn mới hiển thị đúng. Đừng mô tả smoke test là kiểm thử trình duyệt thực tế. Sau khi thay ảnh bằng bản mới, phải chạy kiểm chứng SHA-256 và tạo lại manifest cho bản phát hành cuối.

Tài liệu: [VIET_TAY.md](VIET_TAY.md) · [HUONG_DAN_WEBSITE.md](HUONG_DAN_WEBSITE.md) · [HUONG_DAN_KIEM_CHUNG_PYTHON_CPP.md](HUONG_DAN_KIEM_CHUNG_PYTHON_CPP.md) · [BAO_CAO_KIEM_CHUNG_MOI.md](BAO_CAO_KIEM_CHUNG_MOI.md).
