# Kiểm thử tích hợp thay đổi CSV trên bản sao tạm

- Giữ nguyên toàn bộ CSV gốc; bản sao SC02 E043 được đổi từ 2052 thành 1000.
- Python lần 1: dữ liệu trước khi đổi; Python lần 2: dữ liệu sau khi đổi.
- C++ đọc cùng dữ liệu đã đổi như Python lần 2: **5/5 PASS**.
- So Python trước đổi và C++ sau đổi: **SC02 FAIL do input khác phiên bản**.
- Thử nghiệm này xác nhận phản ứng với thay đổi CSV và chức năng so sánh;
  không chứng minh mã tự tìm được lỗi thuật toán khi hai bên dùng cùng đầu vào sai.

| Đối chiếu | SC02 Max-Flow |
|---|---:|
| Python trước đổi | 7145 |
| Python sau đổi | 6360 |
| C++ sau đổi | 6360 |
| Sai lệch hai phiên bản dữ liệu | 785 |
