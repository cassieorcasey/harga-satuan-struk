# Pencari Harga Satuan dari Struk (SPLTV)

Menghitung harga satuan 3 barang dari 3 struk belanja yang berisi barang sama dengan jumlah berbeda.

## Model

Tiap struk menjadi satu persamaan:

```
a1·x + b1·y + c1·z = T1
a2·x + b2·y + c2·z = T2
a3·x + b3·y + c3·z = T3
```

`a, b, c` = jumlah barang, `T` = total struk, `x, y, z` = harga satuan. Bentuk matriks: `A·X = B`, diselesaikan dengan solver dari [linear-algebra-from-scratch](https://github.com/cassieorcasey/linear-algebra-from-scratch).

## Contoh

| Struk | Kopi | Roti | Susu | Total |
|---|---|---|---|---|
| 1 | 2 | 1 | 1 | 55.000 |
| 2 | 1 | 2 | 3 | 60.000 |
| 3 | 3 | 1 | 2 | 85.000 |

Hasil: Kopi Rp20.000, Roti Rp5.000, Susu Rp10.000.

## Pakai

```bash
pip install -r requirements.txt
python cli.py
```

Total bisa ditulis `55000`, `55.000`, atau `Rp 55.000`. Jumlah boleh desimal (`0,5`).

Dari kode:

```python
from harga_satuan import format_rupiah, hitung_harga_satuan

hasil = hitung_harga_satuan(
    [[2, 1, 1], [1, 2, 3], [3, 1, 2]],
    [55000, 60000, 85000],
    ("Kopi", "Roti", "Susu"),
)
{n: format_rupiah(h) for n, h in hasil.harga.items()}
# {'Kopi': 'Rp20.000', 'Roti': 'Rp5.000', 'Susu': 'Rp10.000'}
hasil.peringatan  # []
```

## Kasus khusus

| Kasus | Hasil |
|---|---|
| Struk identik, berkelipatan, atau hampir berkelipatan | `TidakAdaSolusiUnik` |
| Barang tidak muncul di struk mana pun | `TidakAdaSolusiUnik`, menyebut nama barang |
| Jumlah negatif / bukan angka, total ≤ 0, nama kosong atau kembar | `InputTidakValid` |
| Harga negatif atau di bawah Rp100 | Peringatan |
| Harga bukan kelipatan Rp100 | Peringatan: mungkin ada diskon atau pajak |

## Belum didukung

OCR foto struk, lebih dari 3 barang, diskon/pajak per barang.

## Struktur

```
harga_satuan.py   fungsi inti
cli.py            antarmuka terminal
linear_solver.py  salinan solver SPLTV
tests/            pytest
```

## Tes

```bash
pytest -q
```
