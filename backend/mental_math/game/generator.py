import random
from dataclasses import dataclass
from uuid import UUID

# Inclusive result bounds per addition band; operand rules are enforced in the generator.
BAND_LIMITS: dict[int, tuple[int, int]] = {0: (0, 10), 1: (0, 10), 2: (11, 20), 3: (0, 20), 4: (0, 50)}


@dataclass(frozen=True)
class GeneratedProblem:
    skill: str
    band: int
    operation: str
    operand_a: int
    operand_b: int
    correct_answer: int


def generate_addition(session_id: UUID, ordinal: int, band: int) -> GeneratedProblem:
    """Deterministic for (session, ordinal) so a retried generation yields the same task."""
    rng = random.Random(f"{session_id}:{ordinal}:addition:{band}")
    if band == 0:
        a, b = rng.randint(0, 5), rng.randint(0, 5)
    elif band == 1:
        a = rng.randint(0, 10)
        b = rng.randint(0, 10 - a)
    elif band == 2:
        a = rng.randint(2, 9)
        b = rng.randint(11 - a, 9)
    elif band == 3:
        a = rng.randint(0, 20)
        b = rng.randint(0, 20 - a)
    elif band == 4:
        a = rng.randint(0, 50)
        b = rng.randint(0, 50 - a)
    else:
        raise ValueError(f"Unsupported addition band {band}")
    return GeneratedProblem(skill="addition", band=band, operation="addition", operand_a=a, operand_b=b, correct_answer=a + b)
