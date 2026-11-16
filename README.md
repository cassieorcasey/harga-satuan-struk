# Pencari Harga Satuan dari Struk (SPLTV)

Dari 3 struk belanja berisi 3 barang yang sama dengan jumlah berbeda, program menghitung harga satuan tiap barang. Tiap struk menjadi satu persamaan `a·x + b·y + c·z = T`, lalu sistemnya diselesaikan dengan solver SPLTV dari [linear-algebra-from-scratch](https://github.com/cassieorcasey/linear-algebra-from-scratch).

## Menjalankan

```bash
pip install -r requirements.txt
python cli.py
```

Total boleh ditulis `55000`, `55.000`, atau `Rp 55.000`. Jumlah boleh desimal, misalnya `0,5`.

## Memakai fungsi inti

```python
from harga_satuan import hitung_harga_satuan, format_rupiah

hasil = hitung_harga_satuan(
    [[2, 1, 1], [1, 2, 3], [3, 1, 2]],   # jumlah tiap barang per struk
    [55000, 60000, 85000],               # total tiap struk
    ("Kopi", "Roti", "Susu"),
)
hasil.harga               # {'Kopi': 20000.0, 'Roti': 5000.0, 'Susu': 10000.0}
hasil.total_hitung_ulang  # verifikasi
hasil.peringatan          # [] bila hasil wajar
```

Input salah melempar `InputTidakValid`. Struk yang kurang bervariasi (determinan nol) atau barang yang tidak pernah muncul melempar `TidakAdaSolusiUnik`. Harga negatif, di bawah Rp100, atau bukan kelipatan Rp100 menghasilkan peringatan.

## Tes

```bash
pytest -q
```
