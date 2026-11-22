# Biên bản sửa lỗi giao diện Minimum Cut

## Lỗi đã xác nhận

- Tệp: `app.py`, trang 5 "Minimum Cut".
- Bảng `cut_rows` được tạo từ `result["cut_edges"]` với cột hiển thị tên **`Capacity`** (chữ C hoa).
- Lệnh tính tổng trước khi sửa lại đọc `e["capacity"]` (chữ c thường) từ `cut_rows`, dẫn đến `KeyError: 'capacity'` khi hiển thị trang.
- Đây là lỗi ánh xạ tên cột ở giao diện; không phải lỗi Edmonds–Karp, Ford–Fulkerson DFS, hay thuật toán tìm Min-Cut.

## Sửa mã nguồn

```python
# app.py – tính Capacity từ đúng khóa của bảng hiển thị
st.write(f'**Tổng dung lượng lát cắt = {sum(e["Capacity"] for e in cut_rows):,} xe/giờ.**')
```

## Kiểm thử sau sửa

- Chạy `python -m unittest discover -s tests -v`: **39/39 bài kiểm thử PASS ở phiên bản hiện hành**, bao gồm các bài kiểm thử hồi quy giao diện trong `test_streamlit_ui_smoke.py`.
- Kiểm thử mới **thực thi cả sáu nhánh trang của `app.py`** với bản thay thế giao diện Streamlit, không chỉ gọi các hàm thuật toán.
- Trang Minimum Cut được thực thi riêng trên cả năm kịch bản. Tổng Capacity hiển thị khớp Min-Cut từng kịch bản: SC01=6.511, SC02=7.145, SC03=6.073, SC04=7.708, SC05=7.401 xe quy ước/giờ.
- Bộ kiểm thử cũ vẫn được giữ nguyên.

**Giới hạn:** Các bài kiểm thử khói sử dụng `StreamlitStub` thay vì chạy một máy chủ Streamlit thật trong trình duyệt. Vì vậy, chúng kiểm tra được lỗi Python tại đường thực thi trang nhưng **không** chứng minh mọi chức năng hiển thị, bố cục và tương tác với widget hoạt động trong trình duyệt. Trước khi chụp minh chứng nộp Chương 5, cần cài `requirements.txt`, chạy `streamlit run app.py` và trực tiếp mở cả sáu trang.
