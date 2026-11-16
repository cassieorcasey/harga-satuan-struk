import pytest

from harga_satuan import InputTidakValid, TidakAdaSolusiUnik, hitung_harga_satuan

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
        hitung_harga_satuan([[2, 1, 1], [2, 1, 1], [3, 1, 2]], [55000, 55000, 85000], NAMA)


def test_struk_berkelipatan_ditolak():
    with pytest.raises(TidakAdaSolusiUnik, match="kurang bervariasi"):
        hitung_harga_satuan([[2, 1, 1], [4, 2, 2], [3, 1, 2]], [55000, 110000, 85000], NAMA)


def test_barang_tidak_pernah_muncul():
    with pytest.raises(TidakAdaSolusiUnik, match="Susu"):
        hitung_harga_satuan([[2, 1, 0], [1, 2, 0], [3, 1, 0]], [45000, 30000, 65000], NAMA)


@pytest.mark.parametrize("jumlah", [
    [[-1, 1, 1], [1, 2, 3], [3, 1, 2]],
    [["a", 1, 1], [1, 2, 3], [3, 1, 2]],
    [[True, 1, 1], [1, 2, 3], [3, 1, 2]],
    [[float("nan"), 1, 1], [1, 2, 3], [3, 1, 2]],
    [[1, 1], [1, 2, 3], [3, 1, 2]],
])
def test_jumlah_tidak_valid(jumlah):
    with pytest.raises(InputTidakValid):
        hitung_harga_satuan(jumlah, TOTAL, NAMA)


@pytest.mark.parametrize("total", [
    [0, 60000, 85000],
    [-5, 60000, 85000],
    [None, 60000, 85000],
    [float("inf"), 60000, 85000],
    [55000, 60000],
])
def test_total_tidak_valid(total):
    with pytest.raises(InputTidakValid):
        hitung_harga_satuan(JUMLAH, total, NAMA)


@pytest.mark.parametrize("nama", [("Kopi", "", "Susu"), ("Kopi", "Kopi", "Susu"), ("Kopi", "Roti")])
def test_nama_tidak_valid(nama):
    with pytest.raises(InputTidakValid):
        hitung_harga_satuan(JUMLAH, TOTAL, nama)


def test_pesan_jumlah_negatif_menyebut_struk_dan_barang():
    with pytest.raises(InputTidakValid, match=r"[Ss]truk 1.*Kopi"):
        hitung_harga_satuan([[-1, 1, 1], [1, 2, 3], [3, 1, 2]], TOTAL, NAMA)


def test_input_array_numpy_diterima():
    import numpy as np
    h = hitung_harga_satuan(np.array(JUMLAH), np.array(TOTAL), NAMA)
    assert h.harga == pytest.approx({"Kopi": 20000, "Roti": 5000, "Susu": 10000})
