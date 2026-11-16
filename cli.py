"""Antarmuka terminal: python cli.py"""
import math
import re
import sys

from harga_satuan import InputTidakValid, TidakAdaSolusiUnik, format_rupiah, hitung_harga_satuan


def baca_angka(teks: str, mode: str) -> float:
    """mode 'jumlah': koma = desimal, >= 0. mode 'total': titik = ribuan, > 0."""
    t = teks.strip()
    if mode == "total":
        t = t.lower().removeprefix("rp").replace(" ", "")
        if re.search(r",\d{3}$", t):
            raise ValueError(f"'{teks}' memakai koma sebagai ribuan, tulis 55.000 atau 55000.")
        t = t.replace(".", "")
    try:
        n = float(t.replace(",", "."))
    except ValueError:
        n = math.nan
    if not math.isfinite(n):
        raise ValueError(f"'{teks}' bukan angka.")
    if mode == "jumlah" and n < 0:
        raise ValueError("Jumlah tidak boleh negatif.")
    if mode == "total" and n <= 0:
        raise ValueError("Total harus lebih dari 0.")
    return n


def main(input_fn=input, print_fn=print) -> int:
    def tanya(prompt, mode):
        while True:
            try:
                return baca_angka(input_fn(prompt), mode)
            except ValueError as e:
                print_fn(f"  {e} Coba lagi.")

    print_fn("Pencari Harga Satuan dari Struk\n")
    nama = []
    for i in range(1, 4):
        while True:
            n = input_fn(f"Nama barang {i} (Enter = Barang {i}): ").strip() or f"Barang {i}"
            if n not in nama:
                break
            print_fn(f"  {n} sudah dipakai. Coba lagi.")
        nama.append(n)

    jumlah, total = [], []
    for s in range(1, 4):
        print_fn(f"\nStruk {s}")
        jumlah.append([tanya(f"  Jumlah {n}: ", "jumlah") for n in nama])
        total.append(tanya("  Total (Rp): ", "total"))

    try:
        hasil = hitung_harga_satuan(jumlah, total, nama)
    except (InputTidakValid, TidakAdaSolusiUnik) as e:
        print_fn(f"\nTidak bisa dihitung: {e}")
        return 1

    print_fn("\nHarga satuan:")
    for n, h in hasil.harga.items():
        print_fn(f"  {n}: {format_rupiah(h)}")
    print_fn("\nVerifikasi (hitung ulang vs struk):")
    for s, (hitung, struk) in enumerate(zip(hasil.total_hitung_ulang, total), start=1):
        print_fn(f"  Struk {s}: {format_rupiah(hitung)} vs {format_rupiah(struk)}")
    for p in hasil.peringatan:
        print_fn(f"\nPeringatan: {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
