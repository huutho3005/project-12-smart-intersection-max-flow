# KIỂM TRA TRƯỚC KHI NỘP – SMART INTERSECTION

## Chạy từ thư mục gốc sau khi giải nén

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python kiem_tra_manifest_sha256.py
python verify_independent_processes.py
streamlit run app.py
```

- `requirements.txt` giới hạn Pandas dưới 3 và Plotly dưới 7; không dùng lệnh cài bản mới nhất không ràng buộc để thay thế.
- `python main.py --all` là chương trình thuật toán CLI, **không** phải lệnh mở website.
- Để kiểm tra giao diện thật, mở `http://localhost:8501` sau khi chạy Streamlit; riêng kiểm thử `pytest` với Streamlit giả lập không thay thế thao tác trình duyệt.
- Các file sinh ra trong `.pytest_cache/` và `__pycache__/` bị bỏ qua trong kiểm tra SHA-256.
- Trước khi ZIP/nộp nên xóa cache cho sạch. Dùng `python kiem_tra_manifest_sha256.py` để xác nhận source và dữ liệu đúng với manifest; **không** chạy lại tạo manifest chỉ để xóa cảnh báo về thay đổi source.
- Cần `g++` hỗ trợ C++17 để chạy kiểm chứng Python–C++ độc lập.
