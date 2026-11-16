# Receipt Unit Price Finder (3-Variable Linear System)

[Bahasa Indonesia](README.md) | **English**

Finds the unit prices of 3 items from 3 receipts that contain the same items in different quantities.

## Model

Each receipt becomes one equation:

```
a1·x + b1·y + c1·z = T1
a2·x + b2·y + c2·z = T2
a3·x + b3·y + c3·z = T3
```

`a, b, c` = item quantities, `T` = receipt total, `x, y, z` = unit prices. In matrix form `A·X = B`, solved with the solver from [linear-algebra-from-scratch](https://github.com/cassieorcasey/linear-algebra-from-scratch).

## Example

| Receipt | Coffee | Bread | Milk | Total |
|---|---|---|---|---|
| 1 | 2 | 1 | 1 | 55,000 |
| 2 | 1 | 2 | 3 | 60,000 |
| 3 | 3 | 1 | 2 | 85,000 |

Result: Coffee Rp20,000, Bread Rp5,000, Milk Rp10,000.

## Usage

```bash
pip install -r requirements.txt
python cli.py
```

The CLI is in Indonesian. Totals use Indonesian notation: `55000`, `55.000`, or `Rp 55.000` (a period separates thousands). Quantities may be decimal, written with a comma (`0,5`).

From code:

```python
from harga_satuan import format_rupiah, hitung_harga_satuan

result = hitung_harga_satuan(
    [[2, 1, 1], [1, 2, 3], [3, 1, 2]],  # quantities, one row per receipt
    [55000, 60000, 85000],              # receipt totals
    ("Coffee", "Bread", "Milk"),
)
{name: format_rupiah(p) for name, p in result.harga.items()}
# {'Coffee': 'Rp20.000', 'Bread': 'Rp5.000', 'Milk': 'Rp10.000'}
result.peringatan  # warnings, [] here
```

`result.harga` holds the prices, `result.total_hitung_ulang` the recomputed totals, `result.peringatan` the warnings.

## Edge cases

| Case | Result |
|---|---|
| Identical, proportional, or nearly proportional receipts | `TidakAdaSolusiUnik` (no unique solution) |
| An item missing from every receipt | `TidakAdaSolusiUnik`, naming the item |
| Negative or non-numeric quantity, total ≤ 0, empty or duplicate name | `InputTidakValid` (invalid input) |
| Negative price or below Rp100 | Warning |
| Price not a multiple of Rp100 | Warning: possibly a discount or tax |

## Not supported

Reading receipt photos (OCR), more than 3 items, per-item discounts or taxes.

## Structure

```
harga_satuan.py   core function
cli.py            terminal interface
linear_solver.py  copy of the linear system solver
tests/            pytest
```

## Tests

```bash
pytest -q
```
