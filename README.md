# vqls library

`vqls library` is a clean restart of this repository focused on a Variational Quantum Linear Solver (VQLS) implementation that targets modern Qiskit APIs (Qiskit `>=2.0.0`).

## What changed

- Repository content was reset and rebuilt around a dedicated VQLS package.
- The implementation avoids deprecated `QuantumInstance`/legacy algorithm glue and uses Qiskit's modern primitives path.
- Imports are explicit and defensive so the package can still be imported in environments where Qiskit is not installed.

## Install

```bash
pip install -e .
```

Optional runtime dependencies for actually running the quantum solver:

```bash
pip install "qiskit>=2.0.0" scipy numpy
```

## Quick start

```python
import numpy as np
from vqls_library import VQLSProblem, VQLSSolver

A = np.array([[1.0, 0.2], [0.2, 1.0]], dtype=float)
b = np.array([1.0, 0.0], dtype=float)

problem = VQLSProblem.from_matrix(A, b)
solver = VQLSSolver(problem, reps=2, seed=7)
result = solver.solve(maxiter=50)

print(result.cost, result.parameters)
```

## Notes

- The provided cost function is a compact, maintainable baseline for VQLS-style workflows rather than a full research-optimized implementation.
- For hardware runs, replace default statevector primitives with provider-backed primitives while keeping the same solver API.
