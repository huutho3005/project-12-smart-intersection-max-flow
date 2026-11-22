# KIỂM CHỨNG PYTHON – C++ ĐỘC LẬP (BƯỚC 11)

## Mục đích
Hai chương trình tự giải cùng năm đồ thị, không đọc output của nhau, không sao chép hay gán trước kết quả. Kết quả và checksum đầu vào được ghi lại để tái lập.

## Cách chạy trên Fedora/Linux

```bash
cd SMART_INTERSECTION_SOURCE_EDGE_CASES_DA_KIEM_CHUNG
python verify_independent_processes.py
```

Cần Python 3.13 hoặc tương thích và `g++` hỗ trợ C++17. Không cần thư viện Python ngoài.

Script thực hiện:
1. Băm SHA-256 `data/Nodes.csv` và 5 file `data/scenarios/SCxx/Edges.csv` (dữ liệu chung trực tiếp). Đồng thời băm **toàn bộ** `.py`, `.cpp`, `.csv`, `.md`, `.txt` trong bản nộp, gồm `Lane_Groups.csv`, `Movements.csv`, `Scenarios.csv`, metadata của từng kịch bản, Edge Cases và các module Python; không băm `outputs/` hoặc `__pycache__/`.
2. Biên dịch `cpp_edmonds_karp.cpp` thành chương trình thực thi tạm thời, lưu log biên dịch.
3. Chạy `python main.py --all --output <thư_mục_tạm>` trong **tiến trình riêng**.
4. Chạy chương trình C++ `--all --data <cùng_thư_mục_data>` trong **tiến trình riêng**.
5. Đọc CSV đầu ra *do mỗi tiến trình tự sinh*, so sánh `max_flow`, `min_cut` và `chênh lệch = Python – C++`.
6. Lưu nhật ký, kết quả so sánh và SHA-256 trong `outputs/kiem_chung_python_cpp_doc_lap/`.
7. Nếu khác nhau: ghi **FAIL**, thoát với mã lỗi; KHÔNG sửa kết quả hay thay giá trị cho bằng nhau.

Có thể chạy trực tiếp, không cần script đối chiếu, để kiểm tra độc lập bằng tay:

```bash
python main.py --all --output outputs/python_moi
# C++ tự đọc cùng Nodes.csv và các Edges.csv
# Dùng thư mục tạm hoặc đặt ek_cpp trong thư mục dự án
g++ -std=c++17 -O2 -Wall -Wextra cpp_edmonds_karp.cpp -o ek_cpp
./ek_cpp --all --data data
```

Ở lệnh Python, bảng `outputs/python_moi/summary.csv` là kết quả do Python sinh; C++ in bảng riêng ra terminal. **Không đưa các số của tiểu luận vào mã Python/C++ làm đầu ra gán sẵn.**

## File chứng cứ

- `PYTHON_RUN.log`: log stdout/stderr của Python.
- `CPP_RUN.log`: log stdout/stderr C++.
- `CPP_COMPILE.log`: lệnh biên dịch, mã lỗi và cảnh báo.
- `PYTHON_RAW_SUMMARY.csv`: đầu ra nguyên gốc từ Python.
- `CPP_RAW_SUMMARY.csv`: đầu ra nguyên gốc từ C++.
- `SO_SANH_PYTHON_CPP_5_KICH_BAN.csv`: bảng so sánh có delta và trạng thái PASS/FAIL.
- `SHA256_DU_LIEU_GOC.csv`: checksum 6 file dữ liệu chung trực tiếp.
- `SHA256_TOAN_BO_SOURCE_DATA.csv`: SHA-256 mọi file mã nguồn, CSV metadata, fixture và tài liệu.
- `MANIFEST.json`: danh sách SHA-256, tổng số file và fingerprint SHA-256 toàn bộ cây source/data.
- `kiem_tra_manifest_sha256.py`: kiểm tra lại checksum và phát hiện file bị thêm/sửa/xóa.
- `BIEN_BAN_KIEM_CHUNG.md`: tóm tắt đưa vào Chương 6.

## Kiểm thử chức năng phát hiện sai khác

```bash
python kiem_tra_co_y_sai_khac.py
```

Đây là kiểm thử GIẢ LẬP một kết quả chênh lệch để xác nhận công cụ trả về `FAIL`. **Không** sử dụng dữ liệu giả lập làm minh chứng số lượng xe. Phép thử này **không tác động vào CSV thật** và không được mô tả thành phép thử thay đổi dữ liệu end-to-end.

Kiểm thử riêng với **CSV bị thay đổi trong thư mục tạm**, không sửa bản gốc:

```bash
python kiem_tra_csv_thay_doi_thuc_te.py
```

Phép thử này thực sự đổi Capacity E043 của SC02 **trong bản sao tạm**, chạy Python và C++ trên đúng bản thay đổi, kiểm tra hai chương trình cùng phản ứng; đồng thời so sánh kết quả Python chạy trước khi đổi với C++ chạy sau khi đổi để xác nhận cảnh báo FAIL do **dữ liệu không đồng nhất**. Đây là thử nghiệm tính toàn vẹn đầu vào, không phải phát hiện bug thuật toán.

## Phạm vi kết luận

Kết quả khớp cho thấy hai triển khai Edmonds–Karp độc lập về *mã nguồn thuật toán*, trên cùng CSV, tính ra cùng nghiệm tối ưu. Không chứng minh dữ liệu Demand/Capacity phản ánh nút giao ngoài thực tế; cả hai vẫn cùng sử dụng mô hình và giả định của nhóm.
