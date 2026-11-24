# Báo cáo kiểm chứng – bản source dùng để nộp

**Trạng thái hiện hành:** `python -m pytest -q` cho **47/47 bài test PASS**. Bộ kiểm thử hiện hành gồm 47 bài, trong đó có 4 bài bổ sung kiểm tra bốn chế độ trực quan hóa, đối chiếu cạnh so với SC02 và đường chạy trang Mô hình. Bốn kiểm thử mới xác nhận tập edge_ids không thay đổi kết quả và giữ nguyên khả năng xử lý cạnh trùng mã, cạnh song song, cạnh đối hướng và clone(). Các kết quả Max-Flow/Min-Cut không thay đổi.

## Những gì đã được kiểm chứng bằng chương trình

- 8 module Python chạy trên 5 bộ dữ liệu SC01–SC05.
- Edmonds–Karp, Ford–Fulkerson DFS và Minimum Cut cho cùng kết quả luồng cực đại ở mỗi kịch bản.
- C++17 tự cài đặt và đọc CSV, đối chiếu trực tiếp Python bằng hai tiến trình riêng, **5/5 kịch bản PASS**.
- `tests/test_streamlit_ui_smoke.py` chạy sáu nhánh giao diện bằng `StreamlitStub`, phát hiện lỗi kiểu `Capacity/capacity`; các phép kiểm tra này **không thay thế thử nghiệm trình duyệt**.
- Cạnh E007 ở SC05 được phân loại bằng metadata nhóm làn không hoạt động; bảng tập S/T có đủ 34 đỉnh.
- Manifest SHA-256 có kiểm tra toàn vẹn source, dữ liệu, tài liệu và các ảnh minh chứng (trừ thư mục sinh tự động như `outputs`, `.pytest_cache`, `__pycache__`).

## Kết quả năm kịch bản

| Kịch bản | Demand | Python Max-Flow | C++ Max-Flow | Min-Cut |
|---|---:|---:|---:|---:|
| SC01 | 6.870 | 6.511 | 6.511 | 6.511 |
| SC02 | 8.932 | 7.145 | 7.145 | 7.145 |
| SC03 | 8.932 | 6.073 | 6.073 | 6.073 |
| SC04 | 8.932 | 7.708 | 7.708 | 7.708 |
| SC05 | 8.932 | 7.401 | 7.401 | 7.401 |

Đơn vị: xe quy ước/giờ. Các kết quả thuộc **mạng luồng giả định**, không phải đo lưu lượng ngoài thực địa.

## Lệnh lặp lại kiểm chứng

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python main.py --all
python verify_independent_processes.py
python kiem_tra_manifest_sha256.py
streamlit run app.py
```

## Giới hạn về trình duyệt

Tài liệu `minh_chung_trinh_duyet/` chứa các **ảnh do người thực hiện cung cấp** từ lần thao tác trình duyệt trước đó. Ảnh Min-Cut được chụp **trước lần sửa nhãn E007**; muốn dùng làm bằng chứng cuối cùng cần chụp lại trang 5 trên bản mới. Môi trường tạo gói này **không cài được Streamlit để chụp ảnh mới** nên không tuyên bố đã kiểm thử trình duyệt độc lập sau sửa.
