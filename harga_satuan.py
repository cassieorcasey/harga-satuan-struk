"""Pencari harga satuan 3 barang dari 3 struk belanja (SPLTV)."""
import math
import numbers
from dataclasses import dataclass

import numpy as np

from linear_solver import selesaikan_spl


class InputTidakValid(ValueError): ...


class TidakAdaSolusiUnik(ValueError): ...


@dataclass
class HasilHarga:
    harga: dict[str, float]
    total_hitung_ulang: list[float]
    peringatan: list[str]


def format_rupiah(nilai: float) -> str:
    """20000.4 -> 'Rp20.000'"""
    n = round(nilai)
    tanda = "-" if n < 0 else ""
    return f"{tanda}Rp{abs(n):,}".replace(",", ".")


def _buat_peringatan(harga: dict[str, float]) -> list[str]:
    peringatan = []
    for n, h in harga.items():
        if h < 0:
            peringatan.append(f"Harga {n} negatif ({format_rupiah(h)}): periksa salah ketik.")
        elif h < 100:
            peringatan.append(f"Harga {n} sangat kecil ({format_rupiah(h)}): periksa lagi datanya.")
    if any(abs(h - round(h / 100) * 100) > 0.5 for h in harga.values()):
        peringatan.append("Ada harga bukan kelipatan Rp100, mungkin ada diskon atau pajak yang tidak dimasukkan.")
    return peringatan


def _angka(nilai) -> bool:
    return isinstance(nilai, numbers.Real) and not isinstance(nilai, bool) and math.isfinite(nilai)


def _validasi(jumlah, total, nama) -> None:
    if len(nama) != 3 or any(not str(n).strip() for n in nama):
        raise InputTidakValid("Isi tepat 3 nama barang, tidak boleh kosong.")
    if len(set(nama)) != 3:
        raise InputTidakValid("Nama barang tidak boleh kembar.")
    if len(jumlah) != 3 or any(len(baris) != 3 for baris in jumlah) or len(total) != 3:
        raise InputTidakValid("Butuh tepat 3 struk, masing-masing berisi jumlah 3 barang dan 1 total.")

    for i, baris in enumerate(jumlah, start=1):
        for n, q in zip(nama, baris):
            if not _angka(q) or q < 0:
                raise InputTidakValid(f"Struk {i}: jumlah {n} harus angka 0 atau lebih, bukan {q!r}.")
    for i, t in enumerate(total, start=1):
        if not _angka(t) or t <= 0:
            raise InputTidakValid(f"Struk {i}: total harus angka lebih dari 0, bukan {t!r}.")


def hitung_harga_satuan(jumlah, total, nama=("x", "y", "z")) -> HasilHarga:
    """jumlah: 3x3, satu baris per struk. total: 3 angka."""
    _validasi(jumlah, total, nama)
    A = np.asarray(jumlah, dtype=float)

    for n, muncul in zip(nama, A.any(axis=0)):
        if not muncul:
            raise TidakAdaSolusiUnik(f"{n} tidak muncul di struk mana pun, harganya tidak bisa dihitung.")

    try:
        X = selesaikan_spl(A, total)
    # AssertionError: cek A @ X == B di solver gagal saat matriks hampir singular
    except (np.linalg.LinAlgError, AssertionError):
        raise TidakAdaSolusiUnik("Struk kurang bervariasi. Tambah struk dengan kombinasi jumlah berbeda.") from None

    harga = dict(zip(nama, X.tolist()))
    return HasilHarga(harga, (A @ X).tolist(), _buat_peringatan(harga))
