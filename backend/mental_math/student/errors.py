"""Deterministic error classification. Precedence: correctness, off_by_one, concatenation, subtraction_confusion, other."""


def classify(problem, answer: int) -> str | None:
    if answer == problem.correct_answer:
        return None
    kind = getattr(problem, "kind", "result")
    if kind in {"count", "match", "subitize", "pattern", "frame", "order", "share", "pick"}:
        return None  # early numeracy scenes have no arithmetic error taxonomy
    if kind in {"compare", "parity", "operator"}:
        return "other"
    if abs(answer - problem.correct_answer) == 1:
        return "off_by_one"
    a, b = problem.operand_a, problem.operand_b
    if answer in {int(f"{a}{b}"), int(f"{b}{a}")}:
        return "concatenation"
    if problem.operation == "addition" and answer == abs(a - b):
        return "subtraction_confusion"
    if problem.operation == "subtraction" and answer == a + b:
        return "subtraction_confusion"
    return "other"
