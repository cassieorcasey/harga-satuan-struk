# Receipt Unit Price Finder

Receipts often show only totals. Given 3 receipts with the same 3 items in different quantities, this tool works out the unit price of each item.

## Example

| Receipt | Coffee | Bread | Milk | Total |
|---|---|---|---|---|
| 1 | 2 | 1 | 1 | Rp55,000 |
| 2 | 1 | 2 | 3 | Rp60,000 |
| 3 | 3 | 1 | 2 | Rp85,000 |

Result: Coffee Rp20,000, Bread Rp5,000, Milk Rp10,000.

## Run

```bash
pip install -r requirements.txt
python cli.py
```

The interface is in Indonesian. Totals use Indonesian notation (`55000`, `55.000` or `Rp 55.000`) and decimal quantities take a comma (`0,5`).

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

`harga` holds the prices, `total_hitung_ulang` the recomputed totals and `peringatan` the warnings.

## How it works

Each receipt is one equation, `a·x + b·y + c·z = T`, where a, b, c are quantities, T is the total and x, y, z are unit prices. The 3×3 system is solved by a small NumPy solver in `linear_solver.py`.

## Design decisions

- **Rank check before solving.** Receipts that repeat the same information have no unique answer, so they are rejected with an explanation.
- **Warnings instead of silent answers.** A negative price, a price below Rp100 or one that is not a multiple of Rp100 usually means a typo, a discount or tax.

| Case | Result |
|---|---|
| Identical or proportional receipts | `TidakAdaSolusiUnik` (no unique solution) |
| An item missing from every receipt | `TidakAdaSolusiUnik`, naming the item |
| Negative or non-numeric quantity, total ≤ 0, empty or duplicate name | `InputTidakValid` (invalid input) |

## Limitations

- Receipts that are nearly, but not exactly, proportional can still be solved and give implausible prices. Check the warnings.
- Exactly 3 items and 3 receipts. No receipt photo reading, and no per-item discounts or taxes.

## Tests

```bash
pytest -q
```

## License

[MIT](LICENSE)
