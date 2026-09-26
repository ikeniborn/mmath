"""API-02 across the whole catalogue: neither the public task nor its hint carries the correct answer."""

from types import SimpleNamespace
from uuid import uuid4

import pytest

from mental_math.game.catalogue import CATALOGUE, generate
from mental_math.game.engine import public_problem
from mental_math.game.hints import render_hint

CASES = [(code, band) for code, skill in CATALOGUE.items() for band in skill.bands]


def issued(code: str, band: int, ordinal: int):
    generated = generate(code, uuid4(), ordinal, band)
    return SimpleNamespace(id=uuid4(), ordinal=ordinal, hinted_at=None, **generated.__dict__)


@pytest.mark.parametrize("code, band", CASES)
def test_public_task_and_hint_only_carry_public_quantities(code, band):
    for ordinal in range(1, 41):
        problem = issued(code, band, ordinal)
        view = public_problem(problem).model_dump()
        public_numbers = {value for value in (view["operand_a"], view["operand_b"]) if value is not None}
        public_numbers |= {value for value in (view["prompt"] or {}).values() if isinstance(value, int)}
        public_numbers |= {term for term in (view["prompt"] or {}).get("terms", []) if isinstance(term, int)}
        if problem.kind == "missing":
            assert view["operand_a" if problem.prompt["blank"] == "a" else "operand_b"] is None
        hint = render_hint(problem)
        if problem.kind in {"missing"} or problem.operation in {"division", "remainder"}:
            # the scaffold is built only from the visible operand and the result / dividend and divisor
            assert {hint.operand_a, hint.operand_b} <= public_numbers | {0}, (code, band, view, hint)
