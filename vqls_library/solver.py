from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize

from .problem import VQLSProblem
from .qiskit_compat import real_amplitudes_class, sparse_pauli_op_class, statevector_estimator_class


@dataclass(frozen=True)
class VQLSResult:
    parameters: np.ndarray
    cost: float
    success: bool
    message: str


class VQLSSolver:
    """Minimal VQLS-style solver wired for Qiskit >= 2 primitives."""

    def __init__(self, problem: VQLSProblem, *, reps: int = 2, seed: int | None = None):
        self.problem = problem
        self.reps = reps
        self.rng = np.random.default_rng(seed)

        RealAmplitudes = real_amplitudes_class()
        SparsePauliOp = sparse_pauli_op_class()

        self.ansatz = RealAmplitudes(problem.num_qubits, reps=reps)
        self.observable = SparsePauliOp.from_operator(problem.matrix)
        self._b_projector = SparsePauliOp.from_operator(np.outer(problem.rhs, problem.rhs.conj()))

    def _cost(self, parameters: np.ndarray) -> float:
        Estimator = statevector_estimator_class()
        estimator = Estimator()

        bound = self.ansatz.assign_parameters(parameters)

        num = estimator.run([(bound, self.observable)]).result()[0].data.evs
        den = estimator.run([(bound, self._b_projector)]).result()[0].data.evs

        denom = np.real_if_close(den)
        if np.isclose(denom, 0.0):
            return float("inf")

        return float(np.real_if_close(1.0 - (num / denom)))

    def solve(self, *, maxiter: int = 200) -> VQLSResult:
        x0 = self.rng.uniform(-np.pi, np.pi, size=self.ansatz.num_parameters)
        res = minimize(self._cost, x0=x0, method="COBYLA", options={"maxiter": maxiter})
        return VQLSResult(
            parameters=np.asarray(res.x, dtype=float),
            cost=float(res.fun),
            success=bool(res.success),
            message=str(res.message),
        )
