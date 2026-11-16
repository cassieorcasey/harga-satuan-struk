# Disalin dari cassieorcasey/linear-algebra-from-scratch, linear-solver.py.
# Bisa diganti dengan solver eliminasi Gauss (ide 4) selama tanda tangannya sama.
import numpy as np


def selesaikan_spl(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Selesaikan A @ X = B; error jika tidak ada solusi unik."""
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)

    if A.ndim != 2 or A.shape[0] != A.shape[1] or A.shape[0] != B.shape[0]:
        raise ValueError("A harus persegi dan ukurannya cocok dengan B.")
    if np.linalg.matrix_rank(A) < A.shape[0]:
        raise np.linalg.LinAlgError("Matriks singular: tidak ada solusi unik.")

    X = np.linalg.solve(A, B)
    assert np.allclose(A @ X, B), "Verifikasi gagal."
    return X
