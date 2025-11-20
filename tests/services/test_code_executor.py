import pytest

from mplm.services.code_executor import safe_exec
from mplm.utils.exceptions import CodeExecutionError


def test_safe_exec_valid_code():
    """有効なコードを実行した場合"""
    globals_ = {}
    locals_ = {}

    code = "result = 1 + 2; result2 = 'abcd'"
    safe_exec(code, globals_, locals_)

    assert locals_["result"] == 3
    assert locals_["result2"] == 'abcd'


def test_safe_exec_invalid_code():
    """無効なコードを実行した場合、CodeExecutionErrorが発生する"""
    globals_ = {}
    locals_ = {}

    code = "result = 1 / 0"  # ゼロ除算

    with pytest.raises(CodeExecutionError, match="Execution failed:"):
        safe_exec(code, globals_, locals_)
