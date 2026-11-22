# Biên bản khắc phục 2 điểm ở trang Minimum Cut – Bản mới

## 1. Sai loại giới hạn ở E007, SC05

- Gốc lỗi: phân loại `E005–E016` theo khoảng ID dẫn đến xem E007 như cạnh Demand, dù `E007: APP_N → LG_N_R`, Capacity=0 vì `LG_N_R` **không hoạt động** ở SC05.
- Sửa: `ui_data.cut_category()` ưu tiên kiểm tra metadata thật: Capacity=0, đỉnh đến thuộc nhóm làn LG, `lane_group_id` khớp và `is_active=0`. Kết quả tại SC05 là **Nhóm làn không hoạt động (SC05)**.
- `ui_data.cut_meaning()` ghi rõ nhóm làn ngừng hoạt động theo kịch bản, **không khẳng định là điểm nghẽn hạ tầng vật lý**.
- SC01–SC04: E007 vẫn thuộc nhóm giới hạn Demand theo dữ liệu của các kịch bản đó.
- Không sửa dữ liệu, thuật toán, Maximum Flow hay cấu trúc lát cắt; E007 vẫn được liệt kê trong lát cắt có Capacity=0 vì thuộc tập cạnh được chọn.

## 2. Tập S và T khó đọc

- `app.py` trang 5 bỏ kiểu in `{ A, B, C ... }` trên một dòng dài.
- Thay bằng **bảng hai cột Tập S / Tập T**, một đỉnh một hàng, có thể cuộn dọc; tiêu đề cột cho biết số đỉnh ở từng tập.
- Hai cột được ghép để dễ xem, **không** có nghĩa rằng hai đỉnh cùng hàng có cạnh nối nhau.

## 3. Kiểm thử

Chạy: `python -m unittest discover -s tests -v`.

- 39/39 bài test pytest PASS ở phiên bản hiện hành (gồm các bài kiểm thử hồi quy bổ sung qua nhiều phiên bản).
- Regression: kiểm tra E007 SC05 và E007 SC01–SC04, kể cả trường hợp Capacity=0 nhưng lane vẫn đang active.
- UI smoke test chạy nhánh trang 5 bằng stub, đọc chính DataFrame hiển thị và kiểm tra cả 5 tập S/T (đủ 34 đỉnh, không trùng/thiếu).
- Chạy lại `verify_independent_processes.py`: Python/C++ vẫn phải cho 5/5 PASS; manifest SHA-256 được tạo lại sau khi sửa source.

**Giới hạn:** UI smoke test không thay việc mở trang Streamlit bằng Chrome và xem cách bảng cuộn trên kích thước màn hình thật.
