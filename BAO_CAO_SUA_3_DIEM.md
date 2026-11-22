# Biên bản khắc phục 3 nhận xét phản biện – SMART INTERSECTION

## 1. `run_edge_cases.py`: định danh cung dư chính xác

- `graph.py` gắn `edge_id`, `arc_type` trực tiếp cho từng cung dư thuận/ngược, giữ liên kết chỉ số `rev`.
- `path_from_parent()` giữ `(u, i)`; `path_arcs()` đọc đúng cung được BFS lựa chọn.
- `edmonds_karp.py` lưu `history[*]["path_arcs"]`; `run_edge_cases.py` dựa vào `arc_type` chứ không xét tên đỉnh.
- `Lich_Su_Duong_Tang.csv` và `augmenting_paths.csv` có cột `selected_residual_arcs`.
- Bài thử hai cạnh gốc `A→C` và `C→A` xác nhận tại lần tăng thứ hai BFS chọn cung **E003 reverse C→A**, chứ không nhầm thành cạnh gốc **E008 forward C→A**. Có kiểm thử thêm trường hợp dùng cung gốc C→A và cạnh song song.

## 2. `VIET_TAY.md`: mã viết tay đầy đủ

- Bổ sung mục 2A: `path_from_parent(g,parent,s,t)`.
- Bổ sung mục 2B: `augment(g,path,delta)`, có kiểm tra dung lượng và `rev`.
- Cả hai nhất quán với `graph.py`, không yêu cầu thư viện ngoài; có giải thích về huỷ luồng trên cung dư ngược.

## 3. SHA-256 bao phủ toàn bộ phiên bản

- `verify_independent_processes.py` vẫn xuất `SHA256_DU_LIEU_GOC.csv` cho 6 file đầu vào cốt lõi.
- Thêm `SHA256_TOAN_BO_SOURCE_DATA.csv` cho **mọi tệp mã Python `.py`** (kể cả module, kiểm thử), **C++ `.cpp`**, toàn bộ CSV của `data/` (Nodes, Edges, Lane_Groups, Movements, Scenarios, cả 5 kịch bản), fixture Edge Cases, reference và tài liệu `.md`/`.txt`.
- `MANIFEST.json` lưu danh sách tệp, SHA-256 từng tệp, số lượng và fingerprint của cây nội dung. Không băm `outputs/`, `__pycache__/` vì chúng được sinh khi chạy và gây vòng phụ thuộc.
- `kiem_tra_manifest_sha256.py` cho phép phát hiện file sửa, xóa hoặc thêm mới sau buổi kiểm chứng.

## 4. Phân biệt hai loại kiểm thử sai khác

- `kiem_tra_co_y_sai_khac.py`: chỉ **giả lập số đầu ra** để kiểm tra `compare()` phát hiện FAIL, không động đến CSV và không chứng minh hai tiến trình chạy trên dữ liệu bị sửa.
- `kiem_tra_csv_thay_doi_thuc_te.py`: **thực sự chỉnh E043 của SC02 từ 2052 xuống 1000 trong thư mục tạm**, chạy Python trước/sau sửa và C++ sau sửa. Khi dùng cùng CSV đã sửa thì Python và C++ vẫn phải khớp; khi cố tình so kết quả trước/sau thì phát hiện FAIL vì đầu vào khác phiên bản. Không sửa file gốc, không đưa số liệu thử nghiệm này vào Chương 7.

## 5. Lệnh kiểm chứng

```bash
python -m unittest discover -s tests -v
python run_edge_cases.py
python main.py --all
python verify_independent_processes.py
python kiem_tra_manifest_sha256.py
python kiem_tra_co_y_sai_khac.py
python kiem_tra_csv_thay_doi_thuc_te.py
```

**Phạm vi kết luận:** Kết quả kiểm chứng thuật toán không thay thế kiểm chứng số liệu giao thông thực địa. Với kiểm thử cố tình tạo hai phiên bản CSV khác nhau, FAIL là dấu hiệu **không đồng nhất đầu vào**, không thể kết luận chương trình Python hoặc C++ có lỗi thuật toán.

## 6. Kết quả chạy lại (phiên bản hiện hành)

- **39/39** bài pytest PASS ở phiên bản hiện hành (mốc 26 là kiểm thử của phiên bản trước).
- **7/7** Edge Cases PASS.
- **5/5** Python–C++ PASS trên cùng SC01–SC05: lần lượt 6511, 7145, 6073, 7708, 7401 (chênh lệch 0).
- SHA-256 bao phủ **67 file**, theo `MANIFEST.json`; công cụ kiểm tra lại phát hiện **0 sai lệch** ngay sau khi chốt gói.
- Thử thay đổi thật SC02 E043 trong bản sao: Python ban đầu 7145; Python/C++ cùng bản đã đổi 6360; so hai phiên bản CSV khác nhau sẽ báo FAIL. Các số này chỉ là **kiểm thử độ nhạy đối với dữ liệu vào**, không thay thế dữ liệu thực nghiệm đã chốt.
