"""Kiểm thử tích hợp với CSV thay đổi THẬT nhưng chỉ trong bản sao tạm.

Chứng minh cả hai thuật toán đọc CSV và tính lại; so sánh phát hiện khác
nhau nếu Python và C++ cố ý nhận HAI PHIÊN BẢN INPUT KHÁC NHAU.
Đây không phải phép thử tạo bug thuật toán và không sửa dữ liệu gốc.
Chạy: python kiem_tra_csv_thay_doi_thuc_te.py
"""
import csv
import hashlib
import io
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from verify_independent_processes import compare, csv_rows

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / 'outputs' / 'kiem_chung_python_cpp_doc_lap'


def execute(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(f'Lỗi: {cmd}\n{p.stdout}\n{p.stderr}')
    return p.stdout


def run_python(temp_root, suffix):
    out = temp_root / ('python_' + suffix)
    execute([sys.executable, str(temp_root / 'main.py'),
             '--all', '--output', str(out)], temp_root)
    return {r['scenario_id']: r for r in csv_rows(out / 'summary.csv')}


def main():
    compiler = shutil.which('g++')
    if not compiler:
        raise RuntimeError('Cần cài g++ hỗ trợ C++17')
    original = ROOT / 'data' / 'scenarios' / 'SC02' / 'Edges.csv'
    initial_hash = hashlib.sha256(original.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix='smart_csv_input_test_') as d:
        temp = Path(d) / 'project_copy'
        shutil.copytree(ROOT, temp, ignore=shutil.ignore_patterns(
            'outputs', '__pycache__', '*.pyc'))
        # Lần 1: Python đọc CSV bình thường.
        py_before = run_python(temp, 'before')

        # Lần 2: thay đổi MỘT CAPACITY thật trong bản sao SC02, không sửa gốc.
        csv_file = temp / 'data' / 'scenarios' / 'SC02' / 'Edges.csv'
        with csv_file.open(encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            columns = reader.fieldnames
            rows = list(reader)
        found = [row for row in rows if row['edge_id'] == 'E043']
        assert len(found) == 1 and found[0]['capacity'] == '2052'
        found[0]['capacity'] = '1000'
        with csv_file.open('w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

        # Hai thuật toán đọc cùng dữ liệu ĐÃ THAY ĐỔI.
        py_after = run_python(temp, 'after')
        exe = temp / 'ek_cpp_test'
        execute([compiler, '-std=c++17', '-O2',
                 str(temp / 'cpp_edmonds_karp.cpp'), '-o', str(exe)], temp)
        stdout = execute([str(exe), '--all', '--data', str(temp / 'data')], temp)
        cpp_after = {r['scenario_id']: r for r in csv.DictReader(io.StringIO(stdout))}

        same_version = compare(py_after, cpp_after)
        if not all(r['ket_qua'] == 'PASS' for r in same_version):
            raise AssertionError('Python/C++ khác nhau dù cùng bản CSV đã đổi')
        if py_before['SC02']['max_flow'] == py_after['SC02']['max_flow']:
            raise AssertionError('Thay đổi E043 chưa ảnh hưởng kết quả SC02')

        # Có chủ đích tạo khác phiên bản INPUT: so Python gốc vs C++ đã đổi.
        # Đây là lỗi dữ liệu không đồng nhất, không phải lỗi code thuật toán.
        different_input = compare(py_before, cpp_after)
        if different_input[1]['ket_qua'] != 'FAIL':
            raise AssertionError('Chưa phát hiện khác phiên bản dữ liệu tại SC02')
        if sum(r['ket_qua'] == 'FAIL' for r in different_input) != 1:
            raise AssertionError('Chỉ SC02 phải khác nhau')

        lines = [
            '# Kiểm thử tích hợp thay đổi CSV trên bản sao tạm', '',
            '- Giữ nguyên toàn bộ CSV gốc; bản sao SC02 E043 được đổi từ 2052 thành 1000.',
            '- Python lần 1: dữ liệu trước khi đổi; Python lần 2: dữ liệu sau khi đổi.',
            '- C++ đọc cùng dữ liệu đã đổi như Python lần 2: **5/5 PASS**.',
            '- So Python trước đổi và C++ sau đổi: **SC02 FAIL do input khác phiên bản**.',
            '- Thử nghiệm này xác nhận phản ứng với thay đổi CSV và chức năng so sánh;',
            '  không chứng minh mã tự tìm được lỗi thuật toán khi hai bên dùng cùng đầu vào sai.',
            '', '| Đối chiếu | SC02 Max-Flow |', '|---|---:|',
            f'| Python trước đổi | {py_before["SC02"]["max_flow"]} |',
            f'| Python sau đổi | {py_after["SC02"]["max_flow"]} |',
            f'| C++ sau đổi | {cpp_after["SC02"]["max_flow"]} |',
            f'| Sai lệch hai phiên bản dữ liệu | {different_input[1]["chenh_lech_python_tru_cpp"]} |'
        ]
    # Ra khỏi thư mục tạm, xác nhận dữ liệu gốc không bị sửa.
    if hashlib.sha256(original.read_bytes()).hexdigest() != initial_hash:
        raise AssertionError('CSV gốc đã bị sửa, không đạt an toàn dữ liệu!')
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / 'KIEM_THU_CSV_THAY_DOI_THAT.md').write_text(
        '\n'.join(lines) + '\n', encoding='utf-8')
    print('PASS: Cả hai thuật toán tính lại từ CSV sửa trong bản sao tạm')
    print(f'  SC02: Python gốc={py_before["SC02"]["max_flow"]}, '
          f'Python sửa={py_after["SC02"]["max_flow"]}, '
          f'C++ sửa={cpp_after["SC02"]["max_flow"]}')
    print('PASS: Cố ý dùng hai phiên bản CSV khác nhau thì so sánh phát hiện FAIL')
    print('PASS: SHA-256 CSV gốc không đổi')


if __name__ == '__main__':
    main()
