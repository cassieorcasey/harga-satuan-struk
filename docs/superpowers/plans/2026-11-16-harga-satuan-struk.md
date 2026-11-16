# Pencari Harga Satuan dari Struk — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven
> development (recommended) or inline execution to implement this plan
> task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dari 3 struk (jumlah 3 barang + total), hitung harga satuan tiap barang dengan solver SPLTV, lengkap dengan validasi, peringatan, dan CLI.

**Architecture:** `linear_solver.py` (salinan solver) → `harga_satuan.py` (fungsi inti murni, tanpa I/O) → `cli.py` (input/print saja). Fungsi inti bisa dipakai ulang di Finite.

**Tech Stack:** Python 3, numpy, pytest.

**Spec:** `docs/superpowers/specs/2026-11-16-harga-satuan-struk-design.md`

## Global Constraints

- Isi fungsi `selesaikan_spl` disalin apa adanya dari `linear-algebra-from-scratch/linear-solver.py`; `main()` tidak ikut.
- Semua pesan untuk pengguna dalam Bahasa Indonesia.
- Error: `InputTidakValid(ValueError)`, `TidakAdaSolusiUnik(ValueError)`.
- Ambang: harga < 0 → peringatan negatif; 0 ≤ harga < 100 → peringatan sangat kecil; `abs(h - round(h/100)*100) > 0.5` → peringatan bukan kelipatan Rp100.
- Harga di `HasilHarga` tidak dibulatkan; pembulatan hanya di `format_rupiah`.
- Format rupiah: `Rp` + ribuan dipisah titik, negatif `-Rp1.500`.

## Review Focus

1. Matriks hampir singular (struk nyaris berkelipatan) → harga absurd; peringatan harus muncul, program tidak crash.
2. Galat floating point (19999.9999999) → tidak boleh memicu peringatan kelipatan; tampil `Rp20.000`.
3. Nilai `bool`, string, `None`, NaN, inf dalam `jumlah`/`total` di fungsi inti → `InputTidakValid`, bukan TypeError mentah.
4. Total berformat Indonesia di CLI (`55.000`, `Rp55.000`, `55000`) dan jumlah desimal (`0,5`) → terbaca benar.
5. Barang tidak muncul di struk mana pun → pesan menyebut nama barang, bukan pesan singular umum.

---

## File Structure

```
harga-satuan-struk/
  linear_solver.py          Task 1
  harga_satuan.py           Task 1, 2
  cli.py                    Task 3
  tests/test_harga_satuan.py Task 1, 2
  tests/test_cli.py         Task 3
  requirements.txt          Task 1
  README.md                 Task 3
```

---

### Task 1: Fungsi inti — hitung, validasi, deteksi tanpa solusi unik

**Files:**
- Create: `linear_solver.py`, `harga_satuan.py`, `requirements.txt`, `tests/test_harga_satuan.py`, `tests/__init__.py` (kosong), `conftest.py` (kosong, agar root masuk sys.path)

**Interfaces:**
- Produces:
  - `class InputTidakValid(ValueError)`, `class TidakAdaSolusiUnik(ValueError)`
  - `@dataclass class HasilHarga: harga: dict[str, float]; total_hitung_ulang: list[float]; peringatan: list[str]`
  - `hitung_harga_satuan(jumlah, total, nama=("x","y","z")) -> HasilHarga`

- [ ] **Step 1: Tulis tes yang gagal**

```python
import pytest
from harga_satuan import hitung_harga_satuan, InputTidakValid, TidakAdaSolusiUnik

NAMA = ("Kopi", "Roti", "Susu")
JUMLAH = [[2, 1, 1], [1, 2, 3], [3, 1, 2]]
TOTAL = [55000, 60000, 85000]

def test_contoh_utama():
    h = hitung_harga_satuan(JUMLAH, TOTAL, NAMA)
    assert h.harga == pytest.approx({"Kopi": 20000, "Roti": 5000, "Susu": 10000})
    assert h.total_hitung_ulang == pytest.approx(TOTAL)
    assert h.peringatan == []

def test_struk_identik_ditolak():
    with pytest.raises(TidakAdaSolusiUnik, match="kurang bervariasi"):
        hitung_harga_satuan([[2,1,1],[2,1,1],[3,1,2]], [55000,55000,85000], NAMA)

def test_struk_berkelipatan_ditolak():
    with pytest.raises(TidakAdaSolusiUnik, match="kurang bervariasi"):
        hitung_harga_satuan([[2,1,1],[4,2,2],[3,1,2]], [55000,110000,85000], NAMA)

def test_barang_tidak_pernah_muncul():
    with pytest.raises(TidakAdaSolusiUnik, match="Susu"):
        hitung_harga_satuan([[2,1,0],[1,2,0],[3,1,0]], [45000,30000,65000], NAMA)

@pytest.mark.parametrize("jumlah", [
    [[-1,1,1],[1,2,3],[3,1,2]],
    [["a",1,1],[1,2,3],[3,1,2]],
    [[True,1,1],[1,2,3],[3,1,2]],
    [[float("nan"),1,1],[1,2,3],[3,1,2]],
    [[1,1],[1,2,3],[3,1,2]],
])
def test_jumlah_tidak_valid(jumlah):
    with pytest.raises(InputTidakValid):
        hitung_harga_satuan(jumlah, TOTAL, NAMA)

@pytest.mark.parametrize("total", [[0,60000,85000], [-5,60000,85000], [None,60000,85000], [float("inf"),60000,85000], [55000,60000]])
def test_total_tidak_valid(total):
    with pytest.raises(InputTidakValid):
        hitung_harga_satuan(JUMLAH, total, NAMA)

@pytest.mark.parametrize("nama", [("Kopi","","Susu"), ("Kopi","Kopi","Susu"), ("Kopi","Roti")])
def test_nama_tidak_valid(nama):
    with pytest.raises(InputTidakValid):
        hitung_harga_satuan(JUMLAH, TOTAL, nama)

def test_pesan_jumlah_negatif_menyebut_struk_dan_barang():
    with pytest.raises(InputTidakValid, match=r"[Ss]truk 1.*Kopi"):
        hitung_harga_satuan([[-1,1,1],[1,2,3],[3,1,2]], TOTAL, NAMA)
```

- [ ] **Step 2: Jalankan, pastikan gagal**
Run: `pytest tests/test_harga_satuan.py -q`
Expected: FAIL / ModuleNotFoundError `harga_satuan`.

- [ ] **Step 3: Implementasi**
`linear_solver.py`: salinan `selesaikan_spl` + komentar asal. `harga_satuan.py`: validasi nama (3, tidak kosong setelah strip, unik), bentuk 3×3 / 3, tiap nilai harus `int|float` bukan `bool`, finite; jumlah ≥ 0; total > 0. Cek kolom nol sebelum solver (pesan menyebut nama barang). Panggil `selesaikan_spl`, ubah `LinAlgError` menjadi `TidakAdaSolusiUnik` ("Struk kurang bervariasi: ... tambah struk dengan kombinasi berbeda."). `peringatan` = `[]` di task ini.

- [ ] **Step 4: Jalankan, pastikan lolos**
Run: `pytest -q` → semua PASS.

- [ ] **Step 5: Commit** `feat: fungsi inti hitung_harga_satuan dengan validasi`

---

### Task 2: Peringatan dan format rupiah

**Files:** Modify `harga_satuan.py`, `tests/test_harga_satuan.py`

**Interfaces:**
- Consumes: `hitung_harga_satuan`, `HasilHarga` (Task 1)
- Produces: `format_rupiah(nilai: float) -> str`; `HasilHarga.peringatan` terisi

- [ ] **Step 1: Tulis tes yang gagal**

```python
from harga_satuan import format_rupiah

@pytest.mark.parametrize("n, s", [(20000.0,"Rp20.000"), (19999.9999999,"Rp20.000"), (1234567.4,"Rp1.234.567"), (0,"Rp0"), (-1500,"-Rp1.500"), (999.5,"Rp1.000")])
def test_format_rupiah(n, s):
    assert format_rupiah(n) == s

def test_harga_negatif_diperingatkan():
    # total struk 2 salah ketik
    h = hitung_harga_satuan(JUMLAH, [55000, 6000, 85000], NAMA)
    assert any("negatif" in p for p in h.peringatan)

def test_harga_sangat_kecil_diperingatkan():
    # Susu = 50
    h = hitung_harga_satuan(JUMLAH, [45050, 30150, 65100], NAMA)
    assert any("Susu" in p and "kecil" in p for p in h.peringatan)

def test_bukan_kelipatan_100_diperingatkan():
    # total kena pajak 11%
    h = hitung_harga_satuan(JUMLAH, [61050, 66600, 94350], NAMA)
    assert any("diskon" in p or "pajak" in p for p in h.peringatan)

def test_galat_float_tidak_memicu_peringatan():
    h = hitung_harga_satuan([[0.1,0.2,0.3],[1,2,3.5],[3,1,2]], [0.1*20000+0.2*5000+0.3*10000, 20000+10000+35000, 85000], NAMA)
    assert h.peringatan == []
```

- [ ] **Step 2: Jalankan, pastikan gagal** — `pytest -q`, Expected: ImportError `format_rupiah` / assert gagal.
- [ ] **Step 3: Implementasi** fungsi `_buat_peringatan(harga: dict) -> list[str]` sesuai ambang Global Constraints; satu pesan per barang per jenis, pesan kelipatan cukup sekali. `format_rupiah` pakai `round()` lalu `f"{n:,}".replace(",", ".")`.
- [ ] **Step 4: Jalankan** — `pytest -q` semua PASS.
- [ ] **Step 5: Commit** `feat: peringatan harga janggal dan format rupiah`

---

### Task 3: CLI interaktif + README

**Files:** Create `cli.py`, `tests/test_cli.py`, `README.md`

**Interfaces:**
- Consumes: `hitung_harga_satuan`, `format_rupiah`, kedua error
- Produces: `baca_angka(teks: str, mode: str) -> float` (mode `"jumlah"` atau `"total"`, `ValueError` bila tak valid); `main(input_fn=input, print_fn=print) -> int` (0 sukses, 1 error dari fungsi inti)

Aturan parsing: jumlah — `,` jadi `.`, harus ≥ 0. Total — buang `Rp`/spasi, hapus `.`, `,` jadi `.`, harus > 0.

- [ ] **Step 1: Tulis tes yang gagal**

```python
import pytest
from cli import baca_angka, main

@pytest.mark.parametrize("t, m, v", [("2","jumlah",2), ("0,5","jumlah",0.5), ("55000","total",55000), ("55.000","total",55000), ("Rp 55.000","total",55000), ("1.234.567,5","total",1234567.5)])
def test_baca_angka(t, m, v):
    assert baca_angka(t, m) == pytest.approx(v)

@pytest.mark.parametrize("t, m", [("abc","jumlah"), ("-1","jumlah"), ("","total"), ("0","total"), ("-5.000","total")])
def test_baca_angka_tolak(t, m):
    with pytest.raises(ValueError):
        baca_angka(t, m)

def jalankan(jawaban):
    it, keluar = iter(jawaban), []
    kode = main(input_fn=lambda _: next(it), print_fn=lambda *a: keluar.append(" ".join(map(str, a))))
    return kode, "\n".join(keluar)

CONTOH = ["Kopi","Roti","Susu", "2","1","1","55.000", "1","2","3","60.000", "3","1","2","85.000"]

def test_alur_contoh_utama():
    kode, out = jalankan(CONTOH)
    assert kode == 0
    assert "Kopi" in out and "Rp20.000" in out and "Rp5.000" in out and "Rp10.000" in out

def test_input_salah_ditanya_ulang():
    kode, out = jalankan(CONTOH[:3] + ["dua", "-1"] + CONTOH[3:])
    assert kode == 0 and "Rp20.000" in out

def test_nama_kosong_pakai_default():
    kode, out = jalankan(["", "", ""] + CONTOH[3:])
    assert "Barang 1" in out

def test_struk_identik_pesan_bukan_traceback():
    kode, out = jalankan(["Kopi","Roti","Susu", "2","1","1","55.000", "2","1","1","55.000", "3","1","2","85.000"])
    assert kode == 1 and "kurang bervariasi" in out
```

- [ ] **Step 2: Jalankan, pastikan gagal** — `pytest tests/test_cli.py -q`, Expected: ModuleNotFoundError `cli`.
- [ ] **Step 3: Implementasi** `cli.py` (nama kembar diminta ulang juga) dan README (cara pakai, contoh, menjalankan tes).
- [ ] **Step 4: Jalankan** — `pytest -q` semua PASS; `printf ... | python cli.py` dengan contoh utama menampilkan Rp20.000/Rp5.000/Rp10.000.
- [ ] **Step 5: Commit** `feat: CLI interaktif dan README`
