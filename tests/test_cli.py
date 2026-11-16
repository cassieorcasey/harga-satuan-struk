import pytest

from cli import baca_angka, main


@pytest.mark.parametrize("t, m, v", [
    ("2", "jumlah", 2),
    ("0,5", "jumlah", 0.5),
    ("55000", "total", 55000),
    ("55.000", "total", 55000),
    ("Rp 55.000", "total", 55000),
    ("1.234.567,5", "total", 1234567.5),
])
def test_baca_angka(t, m, v):
    assert baca_angka(t, m) == pytest.approx(v)


@pytest.mark.parametrize("t, m", [("abc", "jumlah"), ("-1", "jumlah"), ("", "total"), ("0", "total"), ("-5.000", "total")])
def test_baca_angka_tolak(t, m):
    with pytest.raises(ValueError):
        baca_angka(t, m)


def jalankan(jawaban):
    it, keluar = iter(jawaban), []
    kode = main(input_fn=lambda _: next(it), print_fn=lambda *a: keluar.append(" ".join(map(str, a))))
    return kode, "\n".join(keluar)


CONTOH = ["Kopi", "Roti", "Susu",
          "2", "1", "1", "55.000",
          "1", "2", "3", "60.000",
          "3", "1", "2", "85.000"]


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


def test_nama_kembar_ditanya_ulang():
    kode, out = jalankan(["Kopi", "Kopi", "Roti", "Susu"] + CONTOH[3:])
    assert kode == 0 and "Susu" in out


def test_struk_identik_pesan_bukan_traceback():
    kode, out = jalankan(["Kopi", "Roti", "Susu",
                          "2", "1", "1", "55.000",
                          "2", "1", "1", "55.000",
                          "3", "1", "2", "85.000"])
    assert kode == 1 and "kurang bervariasi" in out


@pytest.mark.parametrize("t, m", [("55,000", "total"), ("Rp 1,250,000", "total"), ("nan", "jumlah"), ("inf", "total")])
def test_baca_angka_tolak_format_inggris_dan_bukan_angka(t, m):
    with pytest.raises(ValueError):
        baca_angka(t, m)
