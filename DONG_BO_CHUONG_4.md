# Cần thống nhất Chương 4 với mã nguồn Python nộp thật

1. **Mục 4.2.3–4.2.4, hàm `build_graph()` trong bản nháp:** Bản nháp minh họa `adj`, `capacity`, `residual` là ba dictionary và từ chối hai cạnh gốc ngược chiều. Source chính thức dùng lớp `FlowGraph` trong `graph.py`, mỗi cạnh gốc tạo **hai cung dư riêng** (`to`, `res`, `rev`), lưu chỉ số cung thuận trong `graph.edges`. Cách này hỗ trợ cả cạnh song song và cạnh gốc ngược chiều. Nếu giữ đoạn code cũ trong Word, ghi rõ là *phiên bản minh họa đơn giản*, không phải mã nguồn chính thức; tốt nhất đồng bộ code trích trong chương với `graph.py`.
2. **Mục 4.3–4.7:** Dùng đúng tên hàm trong gói: `bfs()`, `edmonds_karp()`, `dfs_path()`, `ford_fulkerson_dfs()`, `min_cut()`. BFS đánh dấu đỉnh bằng `parent[v]=(u,i)`, với `i` là chỉ số cung dư, không chỉ là đỉnh cha.
3. **Kiểm chứng mục 4.8:** `validator.py` kiểm tra `0 <= Flow <= Capacity` trên **44 cạnh gốc**, bảo toàn luồng trên 32 đỉnh trung gian, không còn đường tăng, Max-Flow = Min-Cut; ngoài ra đối chiếu Demand từng movement và metadata SC04/SC05.
4. **Mục 4.9 – độ phức tạp:** BFS/DFS một lượt `O(V+E)`, Edmonds–Karp `O(VE²)`, Ford–Fulkerson DFS với Capacity nguyên `O(E×|f*|)`. Bộ nhớ trạng thái mạng dư + BFS là `O(V+E)`, chưa tính lịch sử các đường tăng và bảng xuất kết quả.
5. **Dữ liệu mô hình:** 34 đỉnh và 44 cạnh **gốc**, 12 movements, 5 kịch bản SC01–SC05. Cung ngược dư không phải hướng xe chạy thực tế. SC05 E019 đổi sang `LG_N_T → MOV_N_R`; metadata SC04/SC05 phải đọc từ file riêng.
6. **Kiểm chứng Python–C++ độc lập (đã bổ sung):** `cpp_edmonds_karp.cpp` là mã C++17 tự đọc `Nodes.csv` và `Edges.csv`, tự cài đặt BFS, cập nhật mạng dư và Minimum Cut, không import/call mã Python. Lệnh `python verify_python_cpp.py` biên dịch bằng `g++` và so sánh trực tiếp kết quả của hai chương trình trên SC01–SC05. Ghi rõ **đã đối chiếu với C++ sau khi thực chạy**, khác với việc so sánh hai thuật toán Python dùng chung cấu trúc `graph.py`.
7. **Lịch sử mạng dư:** `edmonds_karp.py` lưu `residual_snapshot` SAU từng lần tăng luồng; `main.py` xuất `outputs/residual_steps.csv` để website hiển thị từng vòng. Đây là lịch sử 88 cung dư/vòng (44 cạnh gốc × 2 hướng), không phải 88 cạnh giao thông thực tế. Tốn thêm `O(kE)` bộ nhớ lịch sử với `k` là số lần tăng.

## Lệnh kiểm tra lại

```bash
python -m unittest discover -s tests -v
python main.py --all
python main.py --scenario SC05 --history
python verify_python_cpp.py
```

**Lưu ý viết tay:** Đồ thị 6 đỉnh, 7 cạnh của mục 6.4 được kiểm thử tại `test_05_reverse_arc_is_needed_for_bfs`; đường tăng thứ hai dùng cung dư ngược `C → A` để hủy luồng trên cạnh gốc `A → C`.
