from mental_math.game.schemas import HintView


def render_hint(problem) -> HintView:
    """Deterministic visual scaffold from the operands; never carries the answer."""
    if problem.band <= 1:
        kind, scale = "counters", 10
    elif problem.band == 2:
        kind, scale = "ten_frame", 20
    else:
        kind, scale = "number_line", 20 if problem.band == 3 else 50
    return HintView(kind=kind, operand_a=problem.operand_a, operand_b=problem.operand_b, scale=scale)
