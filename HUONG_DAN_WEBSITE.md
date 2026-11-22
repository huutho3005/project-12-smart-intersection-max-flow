# SMART INTERSECTION – Website 6 trang (Bước 14)

## Mục tiêu

Website chỉ là **giao diện minh họa**, toàn bộ phép tính gọi **trực tiếp** 8 module đã kiểm chứng từ Bước 4–13. Không có kết quả SC01–SC05 gán cứng trong `app.py`.

## Chạy website

```bash
cd SMART_INTERSECTION_SOURCE_ON_DINH_DE_NOP
python -m pip install -r requirements.txt
streamlit run app.py
```

Mở địa chỉ Streamlit in ra trong Terminal (thường là http://localhost:8501).

## Sáu trang

1. **Tổng quan:** tổng số Nodes/Edges/Movements/Scenarios thực đọc từ file; Demand, Maximum Flow, Minimum Cut.
2. **Mô hình:** đồ thị 34 đỉnh/44 cạnh theo 6 lớp; lọc theo hướng; hover cạnh để xem Capacity.
3. **Chọn Scenario:** SC01–SC05, metadata `Lane_Groups.csv` và `Movements.csv`; liệt kê thay đổi so với SC02.
4. **Edmonds–Karp:** nhấn nút chạy thật; xem tất cả vòng tăng, bottleneck, tổng luồng, đường tăng; phát lại mạng dư sau từng vòng và cung BFS đã chọn.
5. **Minimum Cut:** tập S, tập T, danh sách cạnh cắt, tổng Capacity, ý nghĩa giao thông; kiểm tra Max-Flow = Min-Cut.
6. **So sánh:** biểu đồ Max-Flow của 5 kịch bản, đối chiếu DFS/BFS/Min-Cut, % chênh lệch so với SC02.

## Nguồn code tính toán thực tế

- `scenario.py`: đọc dữ liệu chuẩn hóa của từng kịch bản; đối chiếu metadata.
- `graph.py`: cung dư thuận/ngược, chỉ số đảo `rev`, cập nhật Residual.
- `bfs.py` + `edmonds_karp.py`: thực thi BFS, đường tăng và lưu snapshot dư từng lần.
- `ford_fulkerson.py`: chạy DFS để đối chiếu từ bản sao mạng độc lập.
- `min_cut.py`: tìm tập S/T trên mạng dư cuối, xác định cạnh gốc đi từ S sang T.
- `validator.py`: kiểm tra các ràng buộc Capacity, Flow Conservation và Max-Flow = Min-Cut.
- `ui_data.py`: **cầu nối**, chỉ gọi lại những module trên và tổng hợp kết quả.
- `ui_graph.py`: chỉ vẽ đồ thị, không tính luồng.
- `app.py`: điều khiển 6 trang.

## Dữ liệu

Đọc từ `data/Scenarios.csv`, `data/Nodes.csv` và ba tệp tại từng `data/scenarios/SCxx/{Edges,Lane_Groups,Movements}.csv`. Số đã chốt của bản nháp:

| Scenario | Demand | Max-Flow | Min-Cut |
|---|---:|---:|---:|
| SC01 | 6.870 | 6.511 | 6.511 |
| SC02 | 8.932 | 7.145 | 7.145 |
| SC03 | 8.932 | 6.073 | 6.073 |
| SC04 | 8.932 | 7.708 | 7.708 |
| SC05 | 8.932 | 7.401 | 7.401 |

Đây là kết quả dự kiến để đối chiếu bằng kiểm thử, **không phải số được hardcode vào website**.

## Kiểm thử sau khi giải nén

```bash
python -m unittest discover -s tests -v
python main.py --all
python verify_independent_processes.py
```

C++ cần trình biên dịch `g++` (C++17). Phần mềm hiện tại là mô hình mạng luồng tĩnh với dữ liệu giả định, không mô phỏng lưu lượng tức thời hoặc pha tín hiệu thực tế.

## Kiểm thử lỗi giao diện Minimum Cut (bổ sung)

Đã sửa `KeyError: 'capacity'` trên trang 5 bằng cách đọc khóa `Capacity` đúng với bảng `cut_rows`. Chạy `python -m unittest discover -s tests -v`; bài `tests/test_streamlit_ui_smoke.py` thực thi đường code của sáu trang bằng `StreamlitStub` và kiểm tra trang Minimum Cut trên SC01–SC05. **Không thay thế** bước mở website thật trong trình duyệt.

## Cập nhật trang 5 – Phân loại E007 và bảng đỉnh S/T

- Ở SC05, E007 Capacity=0 được ghi **Nhóm làn không hoạt động (SC05)**, do metadata `LG_N_R.is_active=0`, không gọi là giới hạn Demand hoặc ùn tắc vật lý.
- Hai tập đỉnh được hiển thị dạng bảng hai cột, **một đỉnh mỗi hàng**, cuộn dọc được; hai đỉnh cùng một hàng không có nghĩa là nối trực tiếp.
- Kiểm tra lại bằng `python -m unittest discover -s tests -v` (39 bài kiểm thử ở phiên bản hiện hành) và mở trực tiếp trang 5 trên Chrome với SC05.
