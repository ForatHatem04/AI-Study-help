"""Compatibility helpers for modern Qiskit primitives (>=2.0.0)."""

from __future__ import annotations

from importlib import import_module


def require_qiskit() -> None:
    try:
        import_module("qiskit")
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "Qiskit is required for quantum execution. Install with `pip install 'qiskit>=2.0.0'`."
        ) from exc


def statevector_estimator_class():
    require_qiskit()
    module = import_module("qiskit.primitives")
    return getattr(module, "StatevectorEstimator")


def real_amplitudes_class():
    require_qiskit()
    module = import_module("qiskit.circuit.library")
    return getattr(module, "RealAmplitudes")


def sparse_pauli_op_class():
    require_qiskit()
    module = import_module("qiskit.quantum_info")
    return getattr(module, "SparsePauliOp")
