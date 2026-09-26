from mental_math.game.early import EARLY_KINDS
from mental_math.game.schemas import HintView


def _scale(*values: int) -> int:
    top = max(values)
    return 10 if top <= 10 else 20 if top <= 20 else 50 if top <= 50 else 100 if top <= 100 else 1000


def render_hint(problem) -> HintView:
    """Deterministic visual scaffold from the operands; never carries the answer.

    Kinds: counters (two groups), pairs (one quantity in twos), ten_frame, number_line, groups (rows), target (from a to b).
    Missing-operand and division tasks only ever send the visible operand and the result, never the blanked answer.
    """
    kind = getattr(problem, "kind", "result")
    a, b, op = problem.operand_a, problem.operand_b, problem.operation
    if kind in EARLY_KINDS:  # the client redraws the scene with scaffolding; nothing beyond the scene itself
        return HintView(kind="scene", operation=op, operand_a=0, operand_b=0, scale=10)
    if kind == "parity":
        return HintView(kind="pairs", operation=op, operand_a=a, operand_b=2, scale=_scale(a))
    if kind in {"compare", "operator"}:
        big = max(a, b, problem.prompt.get("result", 0) if problem.prompt else 0)
        return HintView(kind="counters" if big <= 20 else "number_line", operation=op, operand_a=a, operand_b=b, scale=_scale(big))
    if kind == "missing":
        result = problem.prompt["result"]
        known = b if problem.prompt["blank"] == "a" else a
        if op == "multiplication":
            return HintView(kind="target", operation=op, operand_a=known, operand_b=result, scale=_scale(result))
        if op == "subtraction" and problem.prompt["blank"] == "a":  # ? - b = result: start at the result, step b forward
            return HintView(kind="number_line", operation="addition", operand_a=result, operand_b=known, scale=_scale(result + known))
        if op == "addition" and problem.prompt["blank"] == "a":  # ? + b = result: start at the result, step b back
            return HintView(kind="number_line", operation="subtraction", operand_a=result, operand_b=known, scale=_scale(result))
        low, high = sorted((known, result))  # a + ? = result, a - ? = result: count the gap
        return HintView(kind="target", operation="addition", operand_a=low, operand_b=high, scale=_scale(high))
    if kind in {"chain", "sequence"}:
        return HintView(kind="number_line", operation=op, operand_a=a, operand_b=b, scale=_scale(a + abs(b) * 3, problem.correct_answer))
    if op in {"division", "remainder"}:  # count jumps of b up to a; the quotient is never sent
        return HintView(kind="target", operation=op, operand_a=b, operand_b=a, scale=_scale(a))
    if op == "multiplication":
        return HintView(kind="groups" if a * b <= 100 else "number_line", operation=op, operand_a=a, operand_b=b, scale=_scale(a * b))
    top = max(a, b, a + b if op == "addition" else a)
    if top <= 10:
        kind_out = "counters"
    elif top <= 20:
        kind_out = "ten_frame" if problem.band == 2 else "counters"
    else:
        kind_out = "number_line"
    return HintView(kind=kind_out, operation=op, operand_a=a, operand_b=b, scale=_scale(top))
