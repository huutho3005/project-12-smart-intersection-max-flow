# Minh chứng Chương 6 – SMART INTERSECTION

**Nguồn:** `benchmark.py` và các tệp `outputs/benchmark/` trong gói source hiện hành; phép đo thời gian là một phép **tái đo** trong môi trường Python 3.13.5, có lưu dữ liệu thô, kết quả tổng hợp và metadata. Phần nâng cấp giao diện không thay đổi hai module thuật toán được benchmark.

## 1. Cấu trúc

- `benchmark.py`: script mới, sử dụng `FlowGraph`, `load_scenario`, `ford_fulkerson_dfs`, `edmonds_karp` của source gốc. Không thay thuật toán của nhóm.
- `outputs/benchmark/benchmark_raw.csv`: từng lần đo theo đợt/lần chạy.
- `outputs/benchmark/benchmark_summary.csv`: trung vị của 9 trung vị theo đợt.
- `outputs/benchmark/benchmark_metadata.json`: môi trường, CPU/RAM, Python và chính xác giao thức đo.
- `doi_chieu_source/`: kết quả Edge Cases, history EC05, bảng so sánh Python–C++, và kiểm chứng đường đầu tiên của DFS/BFS.
- `fixture/EC05_7_canh.csv`: đồ thị tính tay 6 đỉnh, 7 cạnh.
- `fixture/do_thi_nho_8_canh.csv`: dữ liệu đồ thị hiệu suất nhỏ 6 đỉnh, 8 cạnh, Maximum Flow 12 với 4 vòng tăng.

## 2. Tái lập

Sau khi giải nén, `benchmark.py`, `graph.py`, `scenario.py` và `data/` đều nằm **ngay thư mục gốc**. Chạy trong thư mục này:

```bash
python benchmark.py --output outputs/benchmark --batches 9 --reps 1000 --large-reps 5 --warmup 20
python verify_benchmark.py
```

- Mạng nhỏ và SC01/SC02: mỗi thuật toán chạy 9 × 1000 lần, khởi động trước 20 lần.
- Mạng lớn (322/440): mỗi thuật toán chạy 9 × 5 lần, khởi động trước 20 lần. Số lần đo này ít hơn và **không nên xem có cùng độ tin cậy thống kê** với mạng trung bình.
- Mỗi lần sử dụng clone riêng, thời gian clone **không nằm trong phép đo**; thời gian chạy trong `edmonds_karp()` **có bao gồm** việc tạo `residual_snapshot` ở từng vòng tăng. DFS chỉ lưu lịch sử giản lược, nên đây là phép so sánh hai hàm source thực tế, **không phải** so sánh công bằng giữa lõi tìm kiếm BFS và DFS.
- Trị số thời gian có thể biến đổi theo điều kiện máy và tải hệ thống. Không áp dụng trực tiếp các số đo trong báo cáo này lên máy khác.

## 3. Những điểm được kiểm chứng

- SC01 đường đầu tiên DFS và BFS giống nhau: `SS -> APP_N -> LG_N_L -> MOV_N_L -> EXIT_E -> TT`, Bottleneck 450.
- Có 7/7 Edge Case PASS, trong đó EC03_A và EC03_B là hai biến thể Capacity = 0.
- Python EK, C++ EK và Min-Cut trùng giá trị trong cả 5 kịch bản (chênh lệch 0).
- Ví dụ EC05 dùng cung dư ngược `C -> A` (cạnh gốc E003), Maximum Flow = Min-Cut = 2.
- Mạng lớn tạo từ 10 bản sao SC01 giữ chung SS/TT: 322 đỉnh, 440 cạnh, Maximum Flow 65.110.

**Cảnh báo phương pháp:** Ở bản Word trước, Bảng 6.27 và Bảng 6.29 có số liệu hiệu suất không có script/log đi kèm; các con số đó đã được thay bằng phép đo có dữ liệu thô và chưa được xác nhận như số liệu đo cũ của nhóm.

## 4. Chú ý về phiên bản nguồn

Các số đo cuối được tạo lại trên source tối ưu `edge_ids`, với SHA-256 các module liên quan ghi trong `outputs/benchmark/benchmark_metadata.json`. Chạy `python verify_benchmark.py` để tính lại trung vị từ 54.090 dòng và đối chiếu summary. Thời gian trên máy khác không nhất thiết giống 6 chữ số thập phân; đây là minh chứng **tái lập quy trình và phép thống kê**, không phải cam kết tốc độ không đổi.
