# Desain: Pencari Harga Satuan dari Struk (SPLTV)

Tanggal: 2026-11-16
Sumber: `ide-pencari-harga-satuan-dari-struk.md` (Ide 2)

## Tujuan

Dari 3 struk belanja (jumlah 3 barang dan total harga tiap struk), program menghitung harga satuan ketiga barang. Fungsi inti harus bisa dipakai ulang di Finite, jadi terpisah dari antarmuka.

## Tidak termasuk (versi pertama)

OCR foto struk, lebih dari 3 barang, diskon/pajak/biaya layanan per barang, penyimpanan hasil ke Finite.

## Pendekatan yang dipertimbangkan

| Pendekatan | Untung | Rugi |
|---|---|---|
| 1. Di repo `linear-algebra-from-scratch`, solver diganti nama | Solver satu sumber | Mengubah repo lama |
| **2. Folder baru, solver disalin (dipilih)** | Proyek mandiri, repo lama tidak tersentuh | Ada dua salinan solver |
| 3. Repo sama, solver dimuat lewat `importlib` | File lama tidak berubah | Kode impor janggal |

Dipilih oleh pemilik proyek: **pendekatan 2**.

## Struktur

```
harga-satuan-struk/
  linear_solver.py        salinan selesaikan_spl dari linear-solver.py, tanpa main()
  harga_satuan.py         fungsi inti + validasi + peringatan
  cli.py                  antarmuka interaktif di terminal
  tests/test_harga_satuan.py
  tests/test_cli.py
  requirements.txt        numpy, pytest
  README.md
```

`linear_solver.py` diberi komentar asal salinannya, supaya mudah ditukar dengan eliminasi Gauss (ide 4) nanti. Isi fungsi `selesaikan_spl` tidak diubah.

## Fungsi inti

```python
hitung_harga_satuan(jumlah, total, nama=("x", "y", "z")) -> HasilHarga
```

- `jumlah`: 3 baris × 3 kolom, jumlah tiap barang di tiap struk.
- `total`: 3 angka, total tiap struk.
- `HasilHarga` (dataclass):
  - `harga`: dict nama → harga satuan (float, belum dibulatkan)
  - `total_hitung_ulang`: 3 angka, total tiap struk dihitung dari harga yang ditemukan
  - `peringatan`: daftar pesan (kosong bila hasil wajar)

Fungsi bantu `format_rupiah(20000.0) -> "Rp20.000"` membulatkan ke rupiah terdekat untuk tampilan.

## Perilaku kasus khusus

| Kasus | Perilaku |
|---|---|
| Bentuk input bukan 3×3 dan 3 total | `InputTidakValid` |
| Jumlah negatif, atau bukan angka (termasuk NaN/tak hingga) | `InputTidakValid`, pesan menyebut struk dan barangnya |
| Total bukan angka atau ≤ 0 | `InputTidakValid` |
| Nama barang kosong atau kembar | `InputTidakValid` |
| Satu barang jumlahnya 0 di semua struk | `TidakAdaSolusiUnik`, pesan menyebut nama barang itu |
| Baris saling bergantung (struk identik/berkelipatan/kombinasi) | `TidakAdaSolusiUnik`: struk kurang bervariasi, tambah struk dengan kombinasi berbeda |
| Harga negatif | Peringatan: tidak masuk akal, periksa salah ketik |
| Harga 0 sampai di bawah Rp100 | Peringatan: harga sangat kecil |
| Harga bukan kelipatan Rp100 (toleransi Rp0,5) | Peringatan: mungkin ada diskon/pajak yang belum dimasukkan |

Kedua kelas error mewarisi `ValueError`. Peringatan tidak menghentikan program; hasil tetap dikembalikan.

## CLI

`python cli.py` menanyakan nama 3 barang (Enter = pakai "Barang 1" dst.), lalu untuk tiap struk: jumlah tiap barang dan total. Input yang bukan angka atau negatif ditanya ulang dengan pesan jelas. Total menerima `55000` maupun `55.000`. Keluaran: harga satuan dalam rupiah, verifikasi per struk (total hitung ulang vs total input), lalu peringatan bila ada. Error dari fungsi inti ditampilkan sebagai pesan, bukan traceback.

## Keputusan yang saya (Claude) buat, bisa diubah

- Jumlah boleh desimal (misal 0,5 kg); hanya negatif dan bukan-angka yang ditolak.
- "Kelipatan wajar" = kelipatan Rp100; "sangat kecil" = di bawah Rp100.
- Kolom nol dilaporkan sebagai tidak ada solusi unik (bukan "harga nol"), karena matriksnya singular.
- Harga inti disimpan tanpa pembulatan; pembulatan hanya di tampilan.
- Tes memakai `pytest`; folder menjadi repo git baru dengan commit per langkah.

## Kasus uji

- Contoh utama: Kopi/Roti/Susu, struk (2,1,1 | 55.000), (1,2,3 | 60.000), (3,1,2 | 85.000) → 20.000 / 5.000 / 10.000, verifikasi cocok, tanpa peringatan.
- Dua struk identik, dua struk berkelipatan → `TidakAdaSolusiUnik`.
- Satu barang tidak muncul di semua struk → `TidakAdaSolusiUnik` dengan nama barang.
- Jumlah negatif, bukan angka, total ≤ 0 → `InputTidakValid`.
- Total salah ketik yang menghasilkan harga negatif → peringatan.
- Total dengan pajak yang menghasilkan harga bukan kelipatan 100 → peringatan.
- CLI: alur contoh utama dari input tiruan, dan tanya-ulang saat input salah.
