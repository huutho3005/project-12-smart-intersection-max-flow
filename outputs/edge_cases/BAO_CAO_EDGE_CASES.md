# KẾT QUẢ KIỂM THỬ EDGE CASES – CHƯƠNG 6.5

Dữ liệu được đọc từ CSV fixtures; các giá trị chuẩn chỉ dùng để kiểm tra.

| Test | Số đỉnh | Số cạnh | Kỳ vọng | BFS | DFS | Min-Cut | BFS vòng | Trạng thái |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| EC01 | 4 | 2 | 0 | 0 | 0 | 0 | 0 | PASS |
| EC02 | 2 | 1 | 7 | 7 | 7 | 7 | 1 | PASS |
| EC03_A | 3 | 2 | 0 | 0 | 0 | 0 | 0 | PASS |
| EC03_B | 4 | 4 | 4 | 4 | 4 | 4 | 1 | PASS |
| EC04 | 4 | 4 | 5 | 5 | 5 | 5 | 2 | PASS |
| EC05 | 6 | 7 | 2 | 2 | 2 | 2 | 2 | PASS |
| EC06 | 7 | 8 | 7 | 7 | 7 | 7 | 3 | PASS |

## Chứng minh cạnh dư ngược tại EC05

- Vòng 1: SS -> A -> C -> TT, Δ=1, tổng F=1; cạnh ngược gốc: không
- Vòng 2: SS -> B -> C -> A -> D -> TT, Δ=1, tổng F=2; cạnh ngược gốc: E003

Sau vòng 1, E003 A->C có dư thuận = 0, dư ngược C->A = 1.
Sau vòng 2, E003 A->C có dư thuận = 1, dư ngược C->A = 0; Flow(E003)=0.

EC03_A (F=0) là bài đơn giản hóa theo yêu cầu người dùng; EC03_B (F=4) là bài đúng mục 6.5.3 của bản nháp.

Mọi trường hợp đã kiểm tra Capacity Constraint, Flow Conservation, BFS không còn đường tăng và Maximum Flow = Minimum Cut.
