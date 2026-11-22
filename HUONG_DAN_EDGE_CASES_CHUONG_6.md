# Bước 9 – Bộ kiểm thử Edge Cases (Chương 6.5)

## 1. Căn cứ nội dung

Dựa theo bản nháp `Chuong_6_Thuc_nghiem_va_kiem_chung_HOAN_CHINH(6).docx`, mục 6.5.1–6.5.6 và ví dụ tính tay mục 6.4. Đề cương Đề tài 12 cũng liệt kê 5 mục 6.5.1–6.5.5. Bộ này bổ sung riêng EC03_A để đáp ứng ví dụ Capacity = 0 khi **không còn nhánh thay thế** mà bạn yêu cầu, trong khi EC03_B bảo toàn trường hợp có nhánh B của báo cáo.

## 2. Cách chạy (không cài thư viện ngoài)

Giải nén ZIP, mở Terminal tại thư mục `SMART_INTERSECTION_SOURCE_EDGE_CASES_DA_KIEM_CHUNG`:

```bash
python run_edge_cases.py
python -m unittest discover -s tests -v
python main.py --all
python report_cut.py
```

- Mỗi Edge Case có dữ liệu `Nodes.csv` và `Edges.csv` trong `tests/fixtures/edge_cases/<MA_CASE>/`.
- `tests/fixtures/edge_cases/cases.csv` ghi kết quả mong đợi để so sánh (không đưa giá trị đó vào thuật toán).
- `run_edge_cases.py` sử dụng đúng 8 module chính, xuất `outputs/edge_cases/Ket_Qua_Edge_Cases.csv`, `Lich_Su_Duong_Tang.csv`, `Residual_Tung_Vong_EC05.csv`, `BAO_CAO_EDGE_CASES.md`.
- `tests/test_edge_cases.py` có 7 bài `unittest` riêng; vẫn giữ 15 bài test trước đó.

## 3. Bảng kết quả chuẩn

| Mã | Trường hợp | Đỉnh | Cạnh | Max-Flow kỳ vọng | Mục báo cáo |
|---|---|---:|---:|---:|---|
| EC01 | Không có đường SS–TT (SS→A; B→TT) | 4 | 2 | 0 | 6.5.1 |
| EC02 | Một cạnh SS→TT (7) | 2 | 1 | 7 | 6.5.2 |
| EC03_A | Chỉ có SS→A (0); A→TT (5) | 3 | 2 | 0 | Ví dụ bổ sung |
| EC03_B | SS→A (0); A→TT (5); SS→B (4); B→TT (4) | 4 | 4 | 4 | 6.5.3 |
| EC04 | Hai đường độc lập, capacity 3 và 2 | 4 | 4 | 5 | 6.5.4 |
| EC05 | 6 đỉnh, 7 cạnh, phải dùng cạnh ngược C→A theo thứ tự BFS | 6 | 7 | 2 | 6.5.5/6.4 |
| EC06 | 2 nguồn S1/S2, 2 đích T1/T2, bổ sung SS/TT | 7 | 8 | 7 | 6.5.6 |

## 4. Chứng minh cạnh ngược EC05

Thứ tự cạnh trong fixtures EC05 phải giữ nguyên để BFS chọn đường 1 trước đường thay thế:

1. `SS → A → C → TT`, bottleneck = 1; sau đó residual ngược `C → A = 1`.
2. `SS → B → C → A → D → TT`, bottleneck = 1; đi qua `C → A` là cung dư ngược của E003 (A→C).
3. Cập nhật vòng 2 làm `flow(E003)` từ 1 trở về 0; `flow(E004)` từ 0 thành 1; Maximum Flow = 2.

Nếu đảo thứ tự các cạnh, BFS có thể đi đường khác ở lần 1, không nhất thiết dùng cạnh ngược. Test này chứng minh **thuật toán có hỗ trợ dùng cạnh ngược trên đường tăng đã được chọn**, không khẳng định mọi cách chọn đường đều phải sử dụng cạnh ngược.

## 5. Phân biệt hai loại test

- Test thuật toán trên mạng nhỏ dùng Capacity đơn vị trừu tượng (đơn vị luồng), **không phải xe/giờ thực tế**.
- Thực nghiệm mô hình giao thông SC01–SC05 ở Chương 6.6, 6.8 dùng CSV riêng, 34 đỉnh/44 cạnh và đơn vị xe quy ước/giờ.

## 6. Những điều cần giải thích lúc vấn đáp

- Vì sao BFS phải kiểm tra `res > 0`?
- Vì sao mạng dư phải có cung ngược?
- Vì sao khi không còn đường tăng thì tối ưu?
- Vì sao thuật toán DFS và BFS phải chạy trên hai bản sao đồ thị?
- Vì sao Max-Flow bằng Min-Cut?
- Vì sao EC03_A có luồng 0 nhưng EC03_B có luồng 4?

## 7. Gợi ý đưa vào Word

Giữ nguyên Bảng 6.7 có 6 trường hợp của bản nháp; trong phần phụ lục D, bổ sung hàng EC03_A làm kiểm thử phụ nhằm phân biệt cầu nối Capacity=0 với trường hợp có đường thay thế. Đính kèm bảng `Ket_Qua_Edge_Cases.csv`, ảnh chụp Terminal (nếu cần) và log riêng EC05 để chứng minh mạng dư.


**Cập nhật sau phản biện:** Trong lịch sử có mốc 22 rồi 26 test khi bổ sung định danh cung dư và manifest; **phiên bản hiện hành có 39 bài pytest**. Trong đó 7 bài liên quan trực tiếp đến Edge Cases. Nhật ký cung dư ngược dùng `history[*]["path_arcs"]`, không còn suy luận từ cặp tên đỉnh.
