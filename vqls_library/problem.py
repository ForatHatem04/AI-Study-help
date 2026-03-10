from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class VQLSProblem:
    """Simple linear-system container for VQLS.

    The system is represented as A x = b, where A is Hermitian (or symmetrized),
    and b is normalized.
    """

    matrix: np.ndarray
    rhs: np.ndarray

    @classmethod
    def from_matrix(cls, matrix: np.ndarray, rhs: np.ndarray, *, symmetrize: bool = True) -> "VQLSProblem":
        mat = np.asarray(matrix, dtype=complex)
        vec = np.asarray(rhs, dtype=complex)

        if mat.ndim != 2 or mat.shape[0] != mat.shape[1]:
            raise ValueError("matrix must be square")
        if vec.ndim != 1 or vec.shape[0] != mat.shape[0]:
            raise ValueError("rhs must be a vector matching matrix dimension")

        if symmetrize and not np.allclose(mat, mat.conj().T):
            mat = 0.5 * (mat + mat.conj().T)

        norm = np.linalg.norm(vec)
        if np.isclose(norm, 0.0):
            raise ValueError("rhs must be non-zero")

        vec = vec / norm
        return cls(matrix=mat, rhs=vec)

    @property
    def num_qubits(self) -> int:
        dim = self.matrix.shape[0]
        n = int(np.log2(dim))
        if 2**n != dim:
            raise ValueError("matrix dimension must be a power of 2")
        return n
