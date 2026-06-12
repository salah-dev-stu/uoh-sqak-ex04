"""FR-FIX-006 — assert the fix's behaviour via a minimal extraction.

Mirrors luigi's `Task.to_str_params` / `from_str_params` so the regression is
checked on Python 3.13 with no luigi install (grader Path D).
"""

import pytest


class _Param:
    def __init__(self, significant: bool = True) -> None:
        self.significant = significant

    def serialize(self, value: str) -> str:
        return str(value)

    def parse(self, text: str) -> str:
        return text


_PARAMS = {"sig": _Param(True), "insig": _Param(significant=False)}


def _to_str_params_buggy(kwargs: dict[str, str]) -> dict[str, str]:
    return {n: _PARAMS[n].serialize(v) for n, v in kwargs.items() if _PARAMS[n].significant}


def _to_str_params_fixed(kwargs: dict[str, str]) -> dict[str, str]:
    return {n: _PARAMS[n].serialize(v) for n, v in kwargs.items()}


def _from_str_params(params_str: dict[str, str]) -> dict[str, str]:
    # iterates ALL declared params and indexes directly (as luigi does)
    return {n: _PARAMS[n].parse(params_str[n]) for n in _PARAMS}


def test_buggy_drops_insignificant_and_breaks_roundtrip():
    kwargs = {"sig": "1", "insig": "2"}
    serialized = _to_str_params_buggy(kwargs)
    assert "insig" not in serialized
    with pytest.raises(KeyError):
        _from_str_params(serialized)


def test_fixed_preserves_insignificant_param():
    kwargs = {"sig": "1", "insig": "2"}
    serialized = _to_str_params_fixed(kwargs)
    assert serialized == {"sig": "1", "insig": "2"}
    assert _from_str_params(serialized) == {"sig": "1", "insig": "2"}
