# Biên bản kiểm chứng hai chương trình độc lập

- Python chạy `main.py` trong tiến trình riêng.
- C++17 được biên dịch từ `cpp_edmonds_karp.cpp`, chạy tiến trình riêng.
- Cả hai tự đọc cùng các file `Nodes.csv` và `scenarios/SCxx/Edges.csv`.
- Giá trị trong bảng lấy trực tiếp từ hai đầu ra mới sinh, KHÔNG được gán cứng.
- SHA256_DU_LIEU_GOC.csv lưu sáu đầu vào cốt lõi dùng chung giữa hai chương trình.
- SHA256_TOAN_BO_SOURCE_DATA.csv và MANIFEST.json lưu SHA-256 mọi module .py,
  mã .cpp, mọi bảng CSV dữ liệu/metadata SC01–SC05, fixture, tài liệu và reference.
- Không băm thư mục outputs vì đó là kết quả chạy có thể tự thay đổi.
- Tổng file theo dõi: 85; fingerprint cây: 565aea51443d90df6817e6e767f4dec1c300617b92826066b01f10eddccea9a3.
- Sai khác sẽ ghi FAIL và chương trình trả mã lỗi; không tự sửa dữ liệu hoặc kết quả.

| Scenario | Python | C++ | Chênh lệch | Min-Cut Python | Min-Cut C++ | Kết quả |
|---|---:|---:|---:|---:|---:|---|
| SC01 | 6,511 | 6,511 | 0 | 6,511 | 6,511 | PASS |
| SC02 | 7,145 | 7,145 | 0 | 7,145 | 7,145 | PASS |
| SC03 | 6,073 | 6,073 | 0 | 6,073 | 6,073 | PASS |
| SC04 | 7,708 | 7,708 | 0 | 7,708 | 7,708 | PASS |
| SC05 | 7,401 | 7,401 | 0 | 7,401 | 7,401 | PASS |

**Kết quả: 5/5 kịch bản đạt.**

Giới hạn: kiểm chứng độc lập mã thuật toán và đọc dữ liệu, không kiểm chứng độ chính xác của Capacity/Demand ngoài thực địa.
