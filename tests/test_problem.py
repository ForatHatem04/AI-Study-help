import numpy as np

from vqls_library.problem import VQLSProblem


def test_problem_normalizes_rhs():
    mat = np.eye(2)
    rhs = np.array([3.0, 4.0])
    problem = VQLSProblem.from_matrix(mat, rhs)
    assert np.isclose(np.linalg.norm(problem.rhs), 1.0)


def test_problem_symmetrizes_matrix():
    mat = np.array([[1.0, 2.0], [0.0, 1.0]])
    rhs = np.array([1.0, 0.0])
    problem = VQLSProblem.from_matrix(mat, rhs)
    assert np.allclose(problem.matrix, problem.matrix.conj().T)
