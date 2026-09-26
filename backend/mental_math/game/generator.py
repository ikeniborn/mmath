from dataclasses import dataclass, field


@dataclass(frozen=True)
class GeneratedProblem:
    """One issued task. `kind` selects the prompt/answer shape; `prompt` carries kind-specific display data.

    kind: result (a op b = ?), missing (blank operand, prompt.blank in {a, b}), chain (sum of signed terms),
    sequence (next term), compare (answer -1/0/1), parity (0 even / 1 odd), operator (0 +, 1 −, 2 ×);
    early numeracy kinds count, match, subitize, pattern, frame, order, share, pick are described in early.py.
    """

    skill: str
    band: int
    operation: str
    operand_a: int
    operand_b: int
    correct_answer: int
    kind: str = "result"
    prompt: dict | None = field(default=None)
