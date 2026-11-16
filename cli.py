"""Antarmuka terminal: python cli.py"""
import sys

from harga_satuan import InputTidakValid, TidakAdaSolusiUnik, format_rupiah, hitung_harga_satuan


def baca_angka(teks: str, mode: str) -> float:
    """mode 'jumlah': koma = desimal, >= 0. mode 'total': titik = ribuan, > 0."""
    t = teks.strip()
    if mode == "total":
        t = t.removeprefix("Rp").removeprefix("rp").replace(" ", "").replace(".", "")
    t = t.replace(",", ".")
    try:
        n = float(t)
    except ValueError:
        raise ValueError(f"'{teks}' bukan angka.") from None
    if mode == "jumlah" and n < 0:
        raise ValueError("Jumlah tidak boleh negatif.")
    if mode == "total" and n <= 0:
        raise ValueError("Total harus lebih dari 0.")
    return n


def _tanya_angka(prompt, mode, input_fn, print_fn) -> float:
    while True:
        try:
            return baca_angka(input_fn(prompt), mode)
        except ValueError as e:
            print_fn(f"  {e} Coba lagi.")


def main(input_fn=input, print_fn=print) -> int:
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
        jumlah.append([_tanya_angka(f"  Jumlah {n}: ", "jumlah", input_fn, print_fn) for n in nama])
        total.append(_tanya_angka("  Total (Rp): ", "total", input_fn, print_fn))

    try:
        hasil = hitung_harga_satuan(jumlah, total, nama)
    except (InputTidakValid, TidakAdaSolusiUnik) as e:
        print_fn(f"\nTidak bisa dihitung: {e}")
        return 1

    print_fn("\nHarga satuan:")
    for n, h in hasil.harga.items():
        print_fn(f"  {n}: {format_rupiah(h)}")
    print_fn("\nVerifikasi (hitung ulang vs struk):")
    for s, (t_hitung, t_struk) in enumerate(zip(hasil.total_hitung_ulang, total), start=1):
        print_fn(f"  Struk {s}: {format_rupiah(t_hitung)} vs {format_rupiah(t_struk)}")
    for p in hasil.peringatan:
        print_fn(f"\nPeringatan: {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
