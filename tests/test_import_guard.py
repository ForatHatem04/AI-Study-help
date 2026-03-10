import pytest

from vqls_library.qiskit_compat import require_qiskit


def test_require_qiskit_raises_without_installation():
    with pytest.raises(RuntimeError):
        require_qiskit()
