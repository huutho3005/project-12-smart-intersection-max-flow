# Phụ lục hình ảnh website SMART INTERSECTION

## Nguồn và phạm vi hình ảnh

- **Ảnh 01–06:** ảnh chụp trình duyệt thật do thành viên nhóm cung cấp ngày 22/11/2026. Đây là ảnh đã có, không phải ảnh mới được chụp trong lần nâng cấp source này.
- **Hình 07–09:** hình minh họa được kết xuất trực tiếp từ dữ liệu SC05/SC02 và các hàm trong `ui_graph.py`; không phải ảnh chụp trình duyệt thật. Các hình này minh họa ba chức năng mới: Flow/Capacity, Residual và so sánh hai kịch bản.

## Danh mục

| Tệp | Nội dung | Nguồn |
|---|---|---|
| 01_Tong_quan.png | Trang Tổng quan | Ảnh chụp trình duyệt do nhóm cung cấp |
| 02_Mo_hinh_do_thi.png | Trang Mô hình đồ thị | Ảnh chụp trình duyệt do nhóm cung cấp |
| 03_Chon_SC05.png | Chọn kịch bản SC05 | Ảnh chụp trình duyệt do nhóm cung cấp |
| 04_Edmonds_Karp_SC05.png | Phát lại Edmonds–Karp | Ảnh chụp trình duyệt do nhóm cung cấp |
| 05_Min_Cut_do_thi.png | Trang Minimum Cut | Ảnh chụp trình duyệt do nhóm cung cấp; cần mở source cuối để xác nhận nội dung E007 hiện hành |
| 06_So_sanh_5_kich_ban.png | Trang So sánh | Ảnh chụp trình duyệt do nhóm cung cấp |
| 07_Mo_hinh_Flow_Capacity.png | Chế độ Flow/Capacity | Kết xuất từ `graph_figure()` |
| 08_Mo_hinh_Residual.png | Mạng dư cuối SC05 | Kết xuất từ `residual_figure()` |
| 09_So_sanh_SC02_SC05.png | So sánh SC02 và SC05 | Kết xuất từ `graph_figure()` và `scenario_edge_changes()` |

Ba hình 07–09 là minh họa đồ họa được sinh từ source, không thay thế việc mở website thật trên máy nộp. Bộ kiểm thử khói cũng không thay thế kiểm thử trình duyệt; trước khi nộp, nhóm cần cài thư viện theo `requirements.txt`, chạy `streamlit run app.py` và xác nhận tương tác thực tế.
