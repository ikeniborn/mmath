from mental_math.game.schemas import HintView


def _scale(*values: int) -> int:
    top = max(values)
    return 10 if top <= 10 else 20 if top <= 20 else 50 if top <= 50 else 100 if top <= 100 else 1000


def render_hint(problem) -> HintView:
    """Deterministic visual scaffold from the operands; never carries the answer.

    Kinds: counters (two groups), pairs (one quantity in twos), ten_frame, number_line, groups (rows).
    """
    kind = getattr(problem, "kind", "result")
    a, b, op = problem.operand_a, problem.operand_b, problem.operation
    if kind == "parity":
        return HintView(kind="pairs", operation=op, operand_a=a, operand_b=2, scale=_scale(a))
    if kind in {"compare", "operator"}:
        big = max(a, b, problem.prompt.get("result", 0) if problem.prompt else 0)
        return HintView(kind="counters" if big <= 20 else "number_line", operation=op, operand_a=a, operand_b=b, scale=_scale(big))
    if kind in {"chain", "sequence"}:
        return HintView(kind="number_line", operation=op, operand_a=a, operand_b=b, scale=_scale(a + abs(b) * 3, problem.correct_answer))
    if op in {"division", "remainder"}:
        return HintView(kind="groups", operation=op, operand_a=b, operand_b=a // b, scale=_scale(a))
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
