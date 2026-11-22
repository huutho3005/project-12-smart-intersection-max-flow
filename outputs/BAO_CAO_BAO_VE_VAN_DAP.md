# Kết quả đối chiếu Ford–Fulkerson DFS, Edmonds–Karp BFS và Minimum Cut

Nguồn: dữ liệu `data/scenarios/SC01–SC05`, thuật toán chạy thật. Đơn vị: xe quy ước/giờ.

| Kịch bản | Demand | BFS | DFS | Min-Cut | Lần tăng BFS/DFS | Đánh giá |
|---|---:|---:|---:|---:|---:|---|
| SC01 | 6,870 | 6,511 | 6,511 | 6,511 | 12/12 | PASS |
| SC02 | 8,932 | 7,145 | 7,145 | 7,145 | 12/12 | PASS |
| SC03 | 8,932 | 6,073 | 6,073 | 6,073 | 12/12 | PASS |
| SC04 | 8,932 | 7,708 | 7,708 | 7,708 | 12/12 | PASS |
| SC05 | 8,932 | 7,401 | 7,401 | 7,401 | 13/15 | PASS |

## Nguồn gốc các giới hạn của lát cắt

| Kịch bản | Demand đầu vào | Nhóm làn | Lối ra | Tổng Min-Cut |
|---|---:|---:|---:|---:|
| SC01 | 3,091 | 3,420 | 0 | 6,511 |
| SC02 | 1,785 | 5,360 | 0 | 7,145 |
| SC03 | 1,785 | 4,288 | 0 | 6,073 |
| SC04 | 924 | 2,680 | 4,104 | 7,708 |
| SC05 | 861 | 4,488 | 2,052 | 7,401 |

## Những lưu ý bắt buộc khi giải thích

- Min-Cut được tìm bằng BFS từ SS trên mạng dư cuối, sau đó lấy cạnh GỐC S -> T.
- Cạnh APP -> LG trong cut thể hiện Demand giới hạn đầu vào; không tự kết luận đó là điểm ùn tắc vật lý.
- SC04: EXIT_N và EXIT_E nằm trong cut, mỗi cạnh có dung lượng 2.052.
- SC05: E007 có Capacity = 0 do làn LG_N_R bị vô hiệu chủ đích, không phải nút thắt vật lý.
- SC05: E006 là cạnh dùng chung T/R và đã đầy, dù không nằm trong lát cắt cụ thể do BFS chọn.
- Có thể tồn tại nhiều lát cắt tối thiểu khác nhau cùng dung lượng.
- DFS và BFS dùng bản sao mạng độc lập. Với dung lượng nguyên không âm, FF dùng DFS kết thúc.
- Hai thuật toán cùng dùng hàm augment() nên kiểm tra DFS/BFS không thay cho kiểm chứng độc lập bằng C++.

## Chuỗi xử lý Minimum Cut

Edmonds-Karp -> Mạng dư cuối -> BFS từ SS qua residual > 0 -> S -> T=V\S -> cạnh gốc S->T -> tổng Capacity.

## Vị trí chèn vào báo cáo

Chương 4.6 (DFS), 4.7 (Min-Cut), 4.8 (kiểm chứng), Chương 6.10 (so sánh), Chương 7.3–7.6 (điểm nghẽn).
