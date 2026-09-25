"""Explicit skill catalogue: code, topic, operation, supported bands, generator and predicates.

Bands follow the shared scale (results within 10 / 10 / bridge ten within 20 / 20 / 50).
Specialised patterns declare only the bands where they are meaningful.
"""

import random
from dataclasses import dataclass
from typing import Callable
from uuid import UUID

from mental_math.game.generator import GeneratedProblem


@dataclass(frozen=True)
class Skill:
    code: str
    topic: str
    operation: str
    bands: tuple[int, ...]
    hint: str  # base hint family; band still refines it in hints.render_hint
    sample: Callable[[random.Random, int], tuple[int, int]]
    check: Callable[[int, int, int], bool]


def _addition(rng: random.Random, band: int) -> tuple[int, int]:
    if band == 0:
        return rng.randint(0, 5), rng.randint(0, 5)
    if band == 1:
        a = rng.randint(0, 10)
        return a, rng.randint(0, 10 - a)
    if band == 2:
        a = rng.randint(2, 9)
        return a, rng.randint(11 - a, 9)
    limit = 20 if band == 3 else 50
    a = rng.randint(0, limit)
    return a, rng.randint(0, limit - a)


def _addition_ok(a: int, b: int, band: int) -> bool:
    total = a + b
    return {0: a <= 5 and b <= 5, 1: total <= 10, 2: a <= 9 and b <= 9 and 11 <= total <= 20, 3: total <= 20, 4: total <= 50}[band]


def _subtraction(rng: random.Random, band: int) -> tuple[int, int]:
    if band == 0:
        a = rng.randint(0, 5)
        return a, rng.randint(0, a)
    if band == 1:
        a = rng.randint(0, 10)
        return a, rng.randint(0, a)
    if band == 2:
        a = rng.randint(11, 18)
        return a, rng.randint(a - 9, 9)
    limit = 20 if band == 3 else 50
    a = rng.randint(0, limit)
    return a, rng.randint(0, a)


def _subtraction_ok(a: int, b: int, band: int) -> bool:
    result = a - b
    return result >= 0 and {0: a <= 5, 1: a <= 10, 2: a > 10 > result >= 1 and b <= 9, 3: a <= 20, 4: a <= 50}[band]


def _doubles(rng: random.Random, band: int) -> tuple[int, int]:
    a = rng.randint(*{1: (1, 5), 3: (6, 10), 4: (11, 25)}[band])
    return a, a


def _near_doubles(rng: random.Random, band: int) -> tuple[int, int]:
    a = rng.randint(*{1: (1, 4), 3: (5, 9), 4: (10, 24)}[band])
    return (a, a + 1) if rng.random() < 0.5 else (a + 1, a)


def _make_ten(rng: random.Random, band: int) -> tuple[int, int]:
    a = rng.randint(1, 9)
    return a, 10 - a


def _times(factor: int, ranges: dict[int, tuple[int, int]]) -> Callable[[random.Random, int], tuple[int, int]]:
    return lambda rng, band: (rng.randint(*ranges[band]), factor)


CATALOGUE: dict[str, Skill] = {
    "addition": Skill("addition", "addition", "addition", (0, 1, 2, 3, 4), "counters", _addition, _addition_ok),
    "subtraction": Skill("subtraction", "subtraction", "subtraction", (0, 1, 2, 3, 4), "counters", _subtraction, _subtraction_ok),
    "doubles": Skill("doubles", "addition", "addition", (1, 3, 4), "counters", _doubles, lambda a, b, band: a == b and _addition_ok(a, b, band)),
    "near_doubles": Skill("near_doubles", "addition", "addition", (1, 3, 4), "counters", _near_doubles, lambda a, b, band: abs(a - b) == 1 and _addition_ok(a, b, band)),
    "make_ten": Skill("make_ten", "addition", "addition", (1,), "ten_frame", _make_ten, lambda a, b, band: a + b == 10 and 1 <= a <= 9),
    "multiplication_2": Skill("multiplication_2", "multiplication", "multiplication", (2, 3), "groups", _times(2, {2: (1, 5), 3: (1, 10)}), lambda a, b, band: b == 2 and a * b <= (10 if band == 2 else 20)),
    "multiplication_3": Skill("multiplication_3", "multiplication", "multiplication", (2, 3, 4), "groups", _times(3, {2: (1, 3), 3: (1, 6), 4: (1, 10)}), lambda a, b, band: b == 3 and a * b <= {2: 9, 3: 18, 4: 30}[band]),
}

OPERATORS = {"addition": lambda a, b: a + b, "subtraction": lambda a, b: a - b, "multiplication": lambda a, b: a * b}


def generate(code: str, session_id: UUID, ordinal: int, band: int) -> GeneratedProblem:
    """Deterministic for (session, ordinal, skill, band) so a retried generation yields the same task."""
    skill = CATALOGUE[code]
    if band not in skill.bands:
        raise ValueError(f"{code} does not support band {band}")
    rng = random.Random(f"{session_id}:{ordinal}:{code}:{band}")
    a, b = skill.sample(rng, band)
    return GeneratedProblem(skill=code, band=band, operation=skill.operation, operand_a=a, operand_b=b, correct_answer=OPERATORS[skill.operation](a, b))


def skills_for_topics(topics: list[str]) -> list[Skill]:
    return [skill for skill in CATALOGUE.values() if skill.topic in topics]


def supported_bands(topics: list[str]) -> list[int]:
    return sorted({band for skill in skills_for_topics(topics) for band in skill.bands})


def clamp_band(code: str, band: int) -> int:
    """Nearest supported band for a skill that does not cover the requested one."""
    bands = CATALOGUE[code].bands
    return min(bands, key=lambda candidate: (abs(candidate - band), candidate))


def eligible_pairs(topics: list[str], mode: str, band: int, automatic_bands: dict[str, int] | None = None) -> list[tuple[str, int]]:
    """(skill, band) pairs a session may issue. Fixed mode locks the band; automatic uses per-skill bands."""
    pairs = []
    for skill in skills_for_topics(topics):
        if mode == "fixed":
            if band in skill.bands:
                pairs.append((skill.code, band))
        else:
            pairs.append((skill.code, (automatic_bands or {}).get(skill.code, clamp_band(skill.code, band))))
    return pairs
