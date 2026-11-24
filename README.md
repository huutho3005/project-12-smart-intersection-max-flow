
# ĐỀ TÀI 12: TÍNH LƯU LƯỢNG PHƯƠNG TIỆN TỐI ĐA CÓ THỂ THÔNG QUA MỘT NÚT GIAO NHIỀU LÀN TRONG GIỜ CAO ĐIỂM

## 1. Giới thiệu đề tài

Đề tài tập trung vào bài toán tính lưu lượng phương tiện tối đa có thể đi qua một nút giao nhiều làn trong giờ cao điểm bằng cách áp dụng kiến thức về đồ thị và mạng luồng.

Nhóm xây dựng mô hình nút giao dưới dạng đồ thị có hướng, trong đó các cạnh được gán dung lượng để biểu diễn khả năng thông hành.

Thuật toán Edmonds–Karp được sử dụng để tìm luồng cực đại. Ngoài ra, nhóm còn cài đặt Ford–Fulkerson sử dụng DFS và phiên bản C++17 để đối chiếu kết quả.

Mô hình gồm:
- 34 đỉnh và 44 cạnh gốc.
- 12 hướng di chuyển (movement).
- 5 kịch bản giao thông từ SC01 đến SC05.
- Website Streamlit gồm 6 trang; trang Mô hình có 4 chế độ trực quan hóa và chức năng so sánh hai kịch bản.

Lưu ý: Dữ liệu Capacity và Demand là số liệu giả định phục vụ mô phỏng, không phải dữ liệu khảo sát giao thông thực tế.

## 2. Công cụ sử dụng

- Python 3.9 trở lên.
- C++17 để kiểm tra kết quả thuật toán.
- Streamlit để xây dựng giao diện.
- Pandas để đọc và xử lý dữ liệu CSV.
- Plotly để trực quan hóa đồ thị.
- Pytest để kiểm thử chương trình.

Các thư viện Python được khai báo trong file `requirements.txt`.

## 3. Cài đặt và chạy chương trình

### 3.1. Cài đặt thư viện

Sau khi tải hoặc clone repository về máy, mở Terminal tại thư mục dự án và chạy:

```bash
python -m pip install -r requirements.txt
```

Nên sử dụng phiên bản thư viện theo giới hạn trong `requirements.txt` để tránh phát sinh lỗi không tương thích.

### 3.2. Chạy website

```bash
streamlit run app.py
```

Sau khi chạy, mở đường dẫn được hiển thị trên Terminal, thông thường là:

http://localhost:8501

Website gồm 6 phần:
1. Tổng quan
2. Mô hình đồ thị
3. Chọn kịch bản
4. Thuật toán Edmonds–Karp
5. Minimum Cut
6. So sánh các kịch bản

Người dùng có thể chọn từng kịch bản; tại trang Mô hình có thể chuyển giữa Capacity, Flow/Capacity, Residual và Minimum Cut, lọc theo hướng và đặt SC02 cạnh kịch bản đang chọn để so sánh.

### 3.3. Chạy thuật toán bằng Terminal

Chạy một kịch bản cụ thể:

```bash
python main.py --scenario SC02 --history
```

Chạy toàn bộ 5 kịch bản:

```bash
python main.py --all
```

Các lệnh này thực hiện tính toán mà không cần mở giao diện Streamlit.

## 4. Thuật toán sử dụng

### 4.1. Edmonds–Karp

Đây là thuật toán chính được sử dụng trong đồ án.

Thuật toán hoạt động dựa trên Ford–Fulkerson nhưng sử dụng BFS để tìm đường tăng luồng trong mạng dư.

Quá trình thực hiện gồm:
1. Tìm đường từ đỉnh nguồn đến đỉnh đích bằng BFS.
2. Xác định dung lượng dư nhỏ nhất trên đường đi.
3. Cập nhật luồng và mạng dư.
4. Tiếp tục cho đến khi không tìm được đường tăng luồng.

Giá trị luồng thu được ở cuối quá trình là Maximum Flow.

### 4.2. Ford–Fulkerson DFS

Nhóm cài đặt thêm phương pháp tìm đường tăng bằng DFS để so sánh với Edmonds–Karp.

Hai phương pháp có thể lựa chọn đường tăng khác nhau nhưng phải cho cùng giá trị luồng cực đại trên cùng một mạng.

### 4.3. Minimum Cut

Sau khi tìm được Maximum Flow, chương trình xác định Minimum Cut dựa trên mạng dư cuối cùng.

Theo định lý Max-Flow Min-Cut, giá trị luồng cực đại bằng dung lượng của lát cắt nhỏ nhất.

Kết quả Minimum Cut giúp xác định các cạnh giới hạn khả năng thông hành trong mô hình.

## 5. Kết quả thực nghiệm

Nhóm thực hiện tính toán trên 5 kịch bản giao thông.

| Kịch bản | Demand | Maximum Flow | Minimum Cut |
|---|---:|---:|---:|
| SC01 - Cơ sở | 6.870 | 6.511 | 6.511 |
| SC02 - Giờ cao điểm | 8.932 | 7.145 | 7.145 |
| SC03 - Suy giảm năng lực | 8.932 | 6.073 | 6.073 |
| SC04 - Bổ sung 2 làn quy đổi | 8.932 | 7.708 | 7.708 |
| SC05 - Điều chỉnh chức năng làn | 8.932 | 7.401 | 7.401 |

Đơn vị: xe quy ước/giờ.

Từ bảng kết quả có thể thấy:

- SC01 là kịch bản cơ sở với lưu lượng cực đại 6.511.
- SC02 có nhu cầu tăng cao nhưng lưu lượng tối đa chỉ đạt 7.145.
- SC03 bị suy giảm năng lực thông hành nên Maximum Flow giảm xuống 6.073.
- SC04 đạt kết quả cao nhất trong 5 kịch bản, với Maximum Flow bằng 7.708.
- SC05 đạt 7.401 sau khi thay đổi cách sử dụng nhóm làn.

Ở cả 5 kịch bản, Maximum Flow đều bằng Minimum Cut, phù hợp với định lý Max-Flow Min-Cut.

Các kết quả trên được tính từ dữ liệu CSV của từng kịch bản.

## 6. Cấu trúc chương trình

Các file chính của dự án:

| File / thư mục | Chức năng |
|---|---|
| `graph.py` | Xây dựng và cập nhật mạng luồng |
| `bfs.py` | Tìm đường tăng bằng BFS |
| `edmonds_karp.py` | Cài đặt thuật toán Edmonds–Karp |
| `ford_fulkerson.py` | Cài đặt Ford–Fulkerson DFS |
| `min_cut.py` | Xác định Minimum Cut |
| `validator.py` | Kiểm tra tính hợp lệ của luồng |
| `scenario.py` | Đọc dữ liệu và xây dựng kịch bản |
| `main.py` | Chạy chương trình bằng Terminal |
| `app.py` | Giao diện chính Streamlit |
| `ui_data.py` | Cầu nối dữ liệu; `scenario_edge_changes()` đối chiếu từng cạnh với SC02 |
| `ui_graph.py` | Hiển thị Capacity, Flow/Capacity, Residual và Minimum Cut; không tính lại luồng |
| `cpp_edmonds_karp.cpp` | Phiên bản thuật toán bằng C++17 |
| `data/` | Dữ liệu đầu vào |
| `tests/` | Các bài kiểm thử |
| `outputs/` | Kết quả sau khi chạy chương trình |
| `minh_chung_trinh_duyet/` | Ảnh minh chứng giao diện website |

Dữ liệu của từng kịch bản được lưu trong `data/scenarios/SC01` đến `SC05`.

## 7. Kiểm thử chương trình

Nhóm sử dụng Pytest để kiểm tra các chức năng chính của chương trình.

Chạy kiểm thử:

```bash
python -m pytest -q
```

Theo kết quả kiểm thử của gói hiện hành, chương trình có 51 bài test đạt yêu cầu (bao gồm kiểm thử màu đường tăng và Minimum Cut).

Ngoài ra, nhóm thực hiện đối chiếu kết quả Python và C++ bằng lệnh:

```bash
python verify_independent_processes.py
```

Kết quả đã ghi nhận cho thấy cả 5 kịch bản đều có giá trị Maximum Flow khớp nhau giữa hai phiên bản.

Để kiểm tra tính toàn vẹn của các file:

```bash
python kiem_tra_manifest_sha256.py
```

Các kết quả kiểm thử và file đầu ra được lưu trong thư mục `outputs/`.

Phần kiểm thử giao diện bằng Streamlit có sử dụng môi trường giả lập. Ảnh chụp từ trình duyệt thực tế được lưu riêng trong thư mục `minh_chung_trinh_duyet/`.

## 8. Giới hạn của đề tài

Mô hình hiện tại chỉ xét mạng luồng tĩnh tại một nút giao, chưa mô phỏng đầy đủ các yếu tố giao thông thực tế như chu kỳ đèn tín hiệu, thời gian chờ hoặc sự thay đổi lưu lượng theo thời gian.

Dung lượng các cạnh được xây dựng dựa trên giả định mô phỏng.

Do đó, kết quả của đồ án chủ yếu phục vụ việc nghiên cứu thuật toán và so sánh các phương án tổ chức làn đường, chưa thể sử dụng trực tiếp để điều khiển giao thông thực tế.

## 9. Tài liệu tham khảo trong dự án

- [VIET_TAY.md](VIET_TAY.md) - Ôn tập thuật toán và ví dụ tính tay.
- [HUONG_DAN_WEBSITE.md](HUONG_DAN_WEBSITE.md) - Hướng dẫn sử dụng website.
- [HUONG_DAN_KIEM_CHUNG_PYTHON_CPP.md](HUONG_DAN_KIEM_CHUNG_PYTHON_CPP.md) - Kiểm chứng kết quả Python và C++.
- [BAO_CAO_KIEM_CHUNG_MOI.md](BAO_CAO_KIEM_CHUNG_MOI.md) - Báo cáo kết quả kiểm thử.

## Chế độ trực quan hóa và so sánh

Trang **Mô hình** hỗ trợ bốn chế độ: Capacity, Flow/Capacity, Residual và Minimum Cut. Người dùng có thể bật so sánh SC02 với kịch bản đang chọn; hai đồ thị dùng cùng vị trí đỉnh và bộ lọc hướng. Hàm `scenario_edge_changes()` nằm trong `ui_data.py`; các hàm dựng hình nằm trong `ui_graph.py`.

Các hình minh họa 07–09 trong `minh_chung_trinh_duyet/` được kết xuất từ source và dữ liệu hiện hành; chúng không được mô tả là ảnh chụp trình duyệt.

### Kiểm tra màu khi trình diễn

- Ở trang **Edmonds–Karp**, khi chọn một vòng tăng luồng, các **cạnh gốc tương ứng với cung dư đã đi qua** được tô cam (`#eb9634`) trên sơ đồ. Các mã cạnh này xuất phát từ `history[...]["path_arcs"]`. Việc tô cạnh gốc không có nghĩa cung dư ngược là chiều xe thực tế; muốn xem chiều cung dư, sử dụng bảng cung dư hoặc chế độ Residual.
- Ở trang **Minimum Cut**, các cạnh thuộc lát cắt được tô đỏ (`#d64141`), trong đó cạnh E007 của SC05 có Capacity bằng 0 vẫn được liệt kê theo phép phân hoạch S/T.
- Trong mã hiện hành, `graph_figure()` phục vụ sơ đồ cạnh gốc ở chế độ Capacity, Flow/Capacity, Minimum Cut và tô đường tăng; riêng hình **cung dư thuận/ngược** được dựng bằng `residual_figure()`. Hai hàm cùng thuộc `ui_graph.py`.
- Chạy `python -m pytest -q tests/test_streamlit_ui_smoke.py tests/test_website_bridge.py` để kiểm tra màu Plotly và lời gọi thực tế của các trang. Kết quả trực tiếp còn được ghi tại `outputs/KIEM_CHUNG_MAU_DUONG_TANG_MINCUT.log`.



## Minh chứng benchmark cho Chương 6 và Chương 7

**Bốn tệp có ngay trong ZIP, không cần tải ZIP minh chứng riêng:**

- `benchmark.py` – script tái đo cả DFS và Edmonds–Karp.
- `outputs/benchmark/benchmark_raw.csv` – 54.090 mẫu thời gian thô.
- `outputs/benchmark/benchmark_summary.csv` – 8 trung vị dùng trong bảng Chương 6 và 7.
- `outputs/benchmark/benchmark_metadata.json` – môi trường, giao thức 9 đợt, SHA-256 của các module được benchmark.

Chạy lệnh tại thư mục chứa `graph.py` và `benchmark.py`:

```bash
python verify_benchmark.py
python benchmark.py --output outputs/benchmark_tai_do --batches 9 --reps 1000 --large-reps 5 --warmup 20
```

Lệnh đầu xác thực dữ liệu benchmark đã nộp mà không ghi đè tệp. Lệnh sau là **tái đo mới** và xuất vào thư mục riêng; thời gian đo mới thay đổi theo cấu hình và tải hệ thống nên không nhất thiết trùng giá trị trong Word.

Lưu ý: hai hàm khác khối lượng ghi history, đặc biệt Edmonds–Karp ghi residual_snapshot sau từng vòng, nên đây là thời gian thực thi **hai cài đặt**, không phải phép so sánh cô lập chi phí BFS và DFS.
