"""Explicit skill catalogue: code, topic, operation, supported bands, generator and predicate.

Bands follow the shared scale (0: within 5–10, 1: within 10, 2: bridging ten within 20, 3: within 20 or 50,
4: within 100, or 1000 for the scaled-facts families). Specialised patterns declare only meaningful bands.
Families follow DfE ready-to-progress NF/AS/MD (Years 1–4), the Russian grade 1–4 mental-arithmetic programme
and soroban chain practice. Word problems, rebuses and numbers above 1000 are out of scope.
"""

import random
from dataclasses import dataclass
from typing import Callable
from uuid import UUID

from mental_math.game.generator import GeneratedProblem

Sample = Callable[[random.Random, int], GeneratedProblem]
Check = Callable[[GeneratedProblem], bool]


@dataclass(frozen=True)
class Skill:
    code: str
    topic: str
    operation: str
    bands: tuple[int, ...]
    sample: Sample
    check: Check


def _p(operation: str, a: int, b: int, answer: int, kind: str = "result", prompt: dict | None = None) -> GeneratedProblem:
    return GeneratedProblem(skill="", band=0, operation=operation, operand_a=a, operand_b=b, correct_answer=answer, kind=kind, prompt=prompt)


def _add(a: int, b: int, kind: str = "result", prompt: dict | None = None) -> GeneratedProblem:
    return _p("addition", a, b, a + b, kind, prompt)


def _sub(a: int, b: int) -> GeneratedProblem:
    return _p("subtraction", a, b, a - b)


def _mul(a: int, b: int) -> GeneratedProblem:
    return _p("multiplication", a, b, a * b)


def _div(a: int, b: int) -> GeneratedProblem:
    return _p("division", a, b, a // b)


LIMIT = {3: 20, 4: 50}


# --- addition -------------------------------------------------------------------------------------------------

def addition(rng: random.Random, band: int) -> GeneratedProblem:
    if band == 0:  # every part is something to count; zero facts are not issued
        return _add(rng.randint(1, 5), rng.randint(1, 5))
    if band == 1:
        a = rng.randint(1, 9)
        return _add(a, rng.randint(1, 10 - a))
    if band == 2:
        a = rng.randint(2, 9)
        return _add(a, rng.randint(11 - a, 9))
    a = rng.randint(1, LIMIT[band] - 1)
    return _add(a, rng.randint(1, LIMIT[band] - a))


def addition_ok(p: GeneratedProblem) -> bool:
    a, b, total = p.operand_a, p.operand_b, p.operand_a + p.operand_b
    return {0: a <= 5 and b <= 5, 1: total <= 10, 2: a <= 9 and b <= 9 and 11 <= total <= 20, 3: total <= 20, 4: total <= 50}[p.band]


def doubles(rng: random.Random, band: int) -> GeneratedProblem:
    a = rng.randint(*{1: (1, 5), 3: (6, 10), 4: (11, 25)}[band])
    return _add(a, a)


def near_doubles(rng: random.Random, band: int) -> GeneratedProblem:
    a = rng.randint(*{1: (1, 4), 3: (5, 9), 4: (10, 24)}[band])
    return _add(a, a + 1) if rng.random() < 0.5 else _add(a + 1, a)


def make_ten(rng: random.Random, band: int) -> GeneratedProblem:
    a = rng.randint(1, 9)
    return _add(a, 10 - a)


def _missing(problem: GeneratedProblem, rng: random.Random) -> GeneratedProblem:
    """Blank one operand: the answer becomes that operand, the result moves into the prompt."""
    blank = rng.choice(["a", "b"])
    if (problem.operand_a if blank == "a" else problem.operand_b) == 0:  # never ask for a missing zero
        blank = "b" if blank == "a" else "a"
    answer = problem.operand_a if blank == "a" else problem.operand_b
    return GeneratedProblem(skill="", band=0, operation=problem.operation, operand_a=problem.operand_a, operand_b=problem.operand_b, correct_answer=answer, kind="missing", prompt={"blank": blank, "result": problem.correct_answer})


def number_bonds(rng: random.Random, band: int) -> GeneratedProblem:
    total = {1: 10, 3: 20, 4: 100}[band]
    a = rng.randint(1, total - 1)
    return _missing(_add(a, total - a), rng)


def missing_addend(rng: random.Random, band: int) -> GeneratedProblem:
    return _missing(addition(rng, band), rng)


def compensation_add(rng: random.Random, band: int) -> GeneratedProblem:
    b = rng.choice([9, 11] if band == 3 else [9, 11, 19, 21, 29, 31])
    limit = 20 if band == 3 else 100
    return _add(rng.randint(1, limit - b), b)


def two_digit_add(rng: random.Random, band: int) -> GeneratedProblem:
    if band == 3:  # tens or ones only, no bridging
        a = rng.randint(11, 89)
        b = rng.choice([10, 20, 30]) if rng.random() < 0.5 else rng.randint(1, 9 - a % 10) if a % 10 < 9 else 10
        return _add(a, b) if a + b <= 100 else _add(a, 10)
    a = rng.randint(11, 89)
    return _add(a, rng.randint(11, 100 - a)) if a <= 89 else _add(a, 10)


def tens_facts_add(rng: random.Random, band: int) -> GeneratedProblem:
    unit = 10 if band == 3 else 100
    a = rng.randint(1, 9)
    return _add(a * unit, rng.randint(1, 10 - a) * unit)


def chain_add(rng: random.Random, band: int) -> GeneratedProblem:
    if band == 2:
        terms = [rng.randint(1, 6) for _ in range(3)]
    elif band == 3:
        terms = [rng.randint(1, 9) for _ in range(3)]
    else:
        terms = [rng.randint(5, 30), rng.randint(1, 20), -rng.randint(1, 15), rng.randint(1, 20)]
    while sum(terms) > (20 if band <= 3 else 100) or any(sum(terms[:i]) < 0 for i in range(1, len(terms) + 1)):
        terms = [max(1, abs(t) - 1) * (1 if t > 0 else -1) for t in terms]
    return GeneratedProblem(skill="", band=0, operation="addition", operand_a=terms[0], operand_b=terms[1], correct_answer=sum(terms), kind="chain", prompt={"terms": terms})


# --- subtraction ----------------------------------------------------------------------------------------------

def subtraction(rng: random.Random, band: int) -> GeneratedProblem:
    if band == 0:  # something is always taken away; the result may be zero
        a = rng.randint(1, 5)
        return _sub(a, rng.randint(1, a))
    if band == 1:
        a = rng.randint(2, 10)
        return _sub(a, rng.randint(1, a))
    if band == 2:
        a = rng.randint(11, 18)
        return _sub(a, rng.randint(a - 9, 9))
    a = rng.randint(2, LIMIT[band])
    return _sub(a, rng.randint(1, a))


def subtraction_ok(p: GeneratedProblem) -> bool:
    a, b, result = p.operand_a, p.operand_b, p.operand_a - p.operand_b
    return result >= 0 and {0: a <= 5, 1: a <= 10, 2: a > 10 > result >= 1 and b <= 9, 3: a <= 20, 4: a <= 50}[p.band]


def count_up(rng: random.Random, band: int) -> GeneratedProblem:
    limit = 20 if band == 3 else 100
    a = rng.randint(6, limit)
    return _sub(a, a - rng.randint(1, 3))


def compensation_sub(rng: random.Random, band: int) -> GeneratedProblem:
    b = rng.choice([9, 11] if band == 3 else [9, 11, 19, 21, 29, 31])
    return _sub(rng.randint(b, 20 if band == 3 else 100), b)


def two_digit_sub(rng: random.Random, band: int) -> GeneratedProblem:
    a = rng.randint(21, 99)
    if band == 3:
        b = rng.choice([10, 20]) if rng.random() < 0.5 else rng.randint(1, a % 10) if a % 10 else 10
        return _sub(a, b)
    return _sub(a, rng.randint(11, a - 1)) if a > 12 else _sub(a, 1)


def tens_facts_sub(rng: random.Random, band: int) -> GeneratedProblem:
    unit = 10 if band == 3 else 100
    a = rng.randint(2, 10)
    return _sub(a * unit, rng.randint(1, a - 1) * unit)


def missing_subtrahend(rng: random.Random, band: int) -> GeneratedProblem:
    return _missing(subtraction(rng, band), rng)


# --- counting -------------------------------------------------------------------------------------------------

def neighbour_one(rng: random.Random, band: int) -> GeneratedProblem:
    limit = {0: 10, 1: 20, 4: 100}[band]
    a = rng.randint(1, limit - 1)
    return _add(a, 1) if rng.random() < 0.5 else _sub(a, 1)


def neighbour_ten(rng: random.Random, band: int) -> GeneratedProblem:
    limit = 50 if band == 3 else 100
    a = rng.randint(10, limit - 10)
    return _add(a, 10) if rng.random() < 0.5 else _sub(a, 10)


def skip_counting(rng: random.Random, band: int) -> GeneratedProblem:
    step = rng.choice({1: [2], 2: [5], 3: [2, 5, 10], 4: [3, 4]}[band])
    limit = {1: 20, 2: 50, 3: 100, 4: 50}[band]
    start = rng.randint(0, (limit - 3 * step) // step) * step
    terms = [start, start + step, start + 2 * step]
    return GeneratedProblem(skill="", band=0, operation="addition", operand_a=terms[-1], operand_b=step, correct_answer=start + 3 * step, kind="sequence", prompt={"terms": terms, "step": step})


def odd_even(rng: random.Random, band: int) -> GeneratedProblem:
    n = rng.randint(1, {0: 10, 1: 20, 4: 100}[band])
    return GeneratedProblem(skill="", band=0, operation="parity", operand_a=n, operand_b=2, correct_answer=n % 2, kind="parity", prompt={"value": n})


def missing_operator(rng: random.Random, band: int) -> GeneratedProblem:
    ops = ["addition", "subtraction"] if band <= 3 else ["addition", "subtraction", "multiplication"]
    limit = {1: 10, 3: 20, 4: 50}[band]
    while True:
        op = rng.choice(ops)
        if op == "addition":
            a = rng.randint(1, limit - 1)
            b = rng.randint(1, limit - a)
            result = a + b
        elif op == "subtraction":
            a = rng.randint(2, limit)
            b = rng.randint(1, a - 1)
            result = a - b
        else:
            a = rng.randint(2, 7)
            b = rng.randint(2, min(7, limit // a))
            result = a * b
        # Exactly one offered operator may produce the result (2 + 2 = 2 x 2 would grade a right answer wrong).
        if sum(value == result for value in [a + b, a - b, a * b][: len(ops)]) == 1:
            break
    return GeneratedProblem(skill="", band=0, operation=op, operand_a=a, operand_b=b, correct_answer={"addition": 0, "subtraction": 1, "multiplication": 2}[op], kind="operator", prompt={"result": result})


# --- multiplication and division ------------------------------------------------------------------------------

def times(factor: int) -> Sample:
    def sample(rng: random.Random, band: int) -> GeneratedProblem:
        high = {2: 3 if factor == 3 else 5, 3: 6 if factor == 3 else (10 if factor == 2 else 5), 4: 10}[band]
        return _mul(rng.randint(1, high), factor)
    return sample


def times_ok(factor: int) -> Check:
    return lambda p: p.operand_b == factor and 1 <= p.operand_a <= 10 and p.correct_answer <= 100


def missing_factor(rng: random.Random, band: int) -> GeneratedProblem:
    factor = rng.randint(2, 10)
    a = rng.randint(1, 5 if band == 3 else 10)
    return _missing(_mul(a, factor), rng)


def repeated_addition(rng: random.Random, band: int) -> GeneratedProblem:
    term = rng.choice([2, 5] if band == 2 else [2, 3, 4, 5, 10])
    count = rng.randint(2, 4 if band == 2 else 5)
    return GeneratedProblem(skill="", band=0, operation="addition", operand_a=term, operand_b=count, correct_answer=term * count, kind="chain", prompt={"terms": [term] * count})


def multiply_by_10(rng: random.Random, band: int) -> GeneratedProblem:
    factor = 10 if band == 3 else rng.choice([10, 100])
    a = rng.randint(1, 10) if factor == 100 or band == 3 else rng.randint(11, 99)
    return _mul(a, factor)


def two_digit_times_one(rng: random.Random, band: int) -> GeneratedProblem:
    b = rng.randint(2, 4)
    return _mul(rng.randint(11, 100 // b), b)


def round_multiply(rng: random.Random, band: int) -> GeneratedProblem:
    b = rng.randint(2, 5)
    return _mul(rng.randint(1, 10 // b) * 10, b)


def halves(rng: random.Random, band: int) -> GeneratedProblem:
    limit = {1: 10, 3: 20, 4: 100}[band]
    return _div(rng.randint(1, limit // 2) * 2, 2)


def divide_by(divisor: int) -> Sample:
    def sample(rng: random.Random, band: int) -> GeneratedProblem:
        return _div(rng.randint(1, 5 if band == 3 else 10) * divisor, divisor)
    return sample


def divide_by_10(rng: random.Random, band: int) -> GeneratedProblem:
    divisor = 10 if band == 3 else rng.choice([10, 100])
    return _div(rng.randint(1, 10 if divisor == 100 else (10 if band == 3 else 99)) * divisor, divisor)


def two_digit_divide(rng: random.Random, band: int) -> GeneratedProblem:
    b = rng.randint(2, 4)
    return _div(rng.randint(11, 100 // b) * b, b)


def division_quotient(rng: random.Random, band: int) -> GeneratedProblem:
    b = rng.randint(2, 9)
    a = rng.randint(b + 1, 99)
    return GeneratedProblem(skill="", band=0, operation="division", operand_a=a, operand_b=b, correct_answer=a // b, kind="result", prompt={"remainder": True})


def remainder(rng: random.Random, band: int) -> GeneratedProblem:
    b = rng.randint(2, 9)
    a = rng.randint(b + 1, 99)
    return GeneratedProblem(skill="", band=0, operation="remainder", operand_a=a, operand_b=b, correct_answer=a % b)


# --- comparison -----------------------------------------------------------------------------------------------

def compare(rng: random.Random, band: int) -> GeneratedProblem:
    limit = {0: 10, 1: 20, 2: 20, 3: 20, 4: 100}[band]

    def expression() -> tuple[str, int]:
        if band <= 1:
            n = rng.randint(0, limit)
            return str(n), n
        a = rng.randint(0, limit)
        if rng.random() < 0.5:
            b = rng.randint(0, limit - a)
            return f"{a} + {b}", a + b
        b = rng.randint(0, a)
        return f"{a} − {b}", a - b

    left_text, left = expression()
    right_text, right = (str(rng.randint(0, limit)), None) if band == 2 else expression()
    right = int(right_text) if right is None else right
    answer = -1 if left < right else 1 if left > right else 0
    return GeneratedProblem(skill="", band=0, operation="compare", operand_a=left, operand_b=right, correct_answer=answer, kind="compare", prompt={"left": left_text, "right": right_text})


# --- catalogue ------------------------------------------------------------------------------------------------

def _within(limit: int) -> Check:
    return lambda p: 0 <= p.correct_answer <= limit and p.operand_a >= 0 and p.operand_b >= 0


def _band_limit(limits: dict[int, int]) -> Check:
    return lambda p: 0 <= p.correct_answer <= limits[p.band] and p.operand_a >= 0 and p.operand_b >= 0


RAW: list[tuple[str, str, str, tuple[int, ...], Sample, Check]] = [
    ("addition", "addition", "addition", (0, 1, 2, 3, 4), addition, addition_ok),
    ("doubles", "addition", "addition", (1, 3, 4), doubles, lambda p: p.operand_a == p.operand_b and addition_ok(p)),
    ("near_doubles", "addition", "addition", (1, 3, 4), near_doubles, lambda p: abs(p.operand_a - p.operand_b) == 1 and addition_ok(p)),
    ("make_ten", "addition", "addition", (1,), make_ten, lambda p: p.operand_a + p.operand_b == 10 and 1 <= p.operand_a <= 9),
    ("number_bonds", "addition", "addition", (1, 3, 4), number_bonds, lambda p: p.kind == "missing" and p.prompt["result"] == {1: 10, 3: 20, 4: 100}[p.band]),
    ("missing_addend", "addition", "addition", (0, 1, 2, 3, 4), missing_addend, lambda p: p.kind == "missing" and addition_ok(p)),
    ("compensation_add", "addition", "addition", (3, 4), compensation_add, lambda p: p.operand_b in {9, 11, 19, 21, 29, 31} and p.correct_answer <= (20 if p.band == 3 else 100)),
    ("two_digit_add", "addition", "addition", (3, 4), two_digit_add, lambda p: 10 < p.operand_a < 100 and p.correct_answer <= 100),
    ("tens_facts_add", "addition", "addition", (3, 4), tens_facts_add, lambda p: p.operand_a % (10 if p.band == 3 else 100) == 0 and p.correct_answer <= (100 if p.band == 3 else 1000)),
    ("chain_add", "addition", "addition", (2, 3, 4), chain_add, lambda p: p.kind == "chain" and len(p.prompt["terms"]) >= 3 and 0 <= p.correct_answer <= (20 if p.band <= 3 else 100)),
    ("subtraction", "subtraction", "subtraction", (0, 1, 2, 3, 4), subtraction, subtraction_ok),
    ("count_up", "subtraction", "subtraction", (3, 4), count_up, lambda p: 1 <= p.correct_answer <= 3 and p.operand_a <= (20 if p.band == 3 else 100)),
    ("compensation_sub", "subtraction", "subtraction", (3, 4), compensation_sub, lambda p: p.operand_b in {9, 11, 19, 21, 29, 31} and p.correct_answer >= 0 and p.operand_a <= (20 if p.band == 3 else 100)),
    ("two_digit_sub", "subtraction", "subtraction", (3, 4), two_digit_sub, lambda p: 20 < p.operand_a < 100 and p.correct_answer >= 0),
    ("tens_facts_sub", "subtraction", "subtraction", (3, 4), tens_facts_sub, lambda p: p.correct_answer > 0 and p.operand_a <= (100 if p.band == 3 else 1000)),
    ("missing_subtrahend", "subtraction", "subtraction", (1, 2, 3, 4), missing_subtrahend, lambda p: p.kind == "missing" and subtraction_ok(p)),
    ("neighbour_one", "counting", "mixed", (0, 1, 4), neighbour_one, lambda p: p.operand_b == 1 and p.correct_answer <= {0: 10, 1: 20, 4: 100}[p.band]),
    ("neighbour_ten", "counting", "mixed", (3, 4), neighbour_ten, lambda p: p.operand_b == 10 and p.correct_answer <= (50 if p.band == 3 else 100)),
    ("skip_counting", "counting", "addition", (1, 2, 3, 4), skip_counting, lambda p: p.kind == "sequence" and p.correct_answer == p.prompt["terms"][-1] + p.prompt["step"] and p.correct_answer <= {1: 20, 2: 50, 3: 100, 4: 50}[p.band]),
    ("odd_even", "counting", "parity", (0, 1, 4), odd_even, lambda p: p.kind == "parity" and p.correct_answer == p.prompt["value"] % 2),
    ("missing_operator", "counting", "mixed", (1, 3, 4), missing_operator, lambda p: p.kind == "operator" and p.correct_answer in {0, 1, 2} and p.prompt["result"] <= {1: 10, 3: 20, 4: 50}[p.band]),
    ("multiplication_2", "multiplication", "multiplication", (2, 3), times(2), lambda p: times_ok(2)(p) and p.correct_answer <= (10 if p.band == 2 else 20)),
    ("multiplication_3", "multiplication", "multiplication", (2, 3, 4), times(3), lambda p: times_ok(3)(p) and p.correct_answer <= {2: 9, 3: 18, 4: 30}[p.band]),
    *[(f"multiplication_{n}", "multiplication", "multiplication", (3, 4), times(n), times_ok(n)) for n in range(4, 11)],
    ("missing_factor", "multiplication", "multiplication", (3, 4), missing_factor, lambda p: p.kind == "missing" and p.prompt["result"] <= 100),
    ("repeated_addition", "multiplication", "addition", (2, 3), repeated_addition, lambda p: p.kind == "chain" and len(set(p.prompt["terms"])) == 1 and p.correct_answer <= (20 if p.band == 2 else 50)),
    ("multiply_by_10", "multiplication", "multiplication", (3, 4), multiply_by_10, lambda p: p.operand_b in {10, 100} and p.correct_answer <= (100 if p.band == 3 else 1000)),
    ("two_digit_times_one", "multiplication", "multiplication", (4,), two_digit_times_one, lambda p: 10 < p.operand_a < 100 and p.correct_answer <= 100),
    ("round_multiply", "multiplication", "multiplication", (4,), round_multiply, lambda p: p.operand_a % 10 == 0 and p.correct_answer <= 100),
    ("halves", "division", "division", (1, 3, 4), halves, lambda p: p.operand_b == 2 and p.operand_a % 2 == 0 and p.operand_a <= {1: 10, 3: 20, 4: 100}[p.band]),
    *[(f"division_{n}", "division", "division", (3, 4), divide_by(n), (lambda n: lambda p: p.operand_b == n and p.operand_a % n == 0 and p.correct_answer <= 10)(n)) for n in range(2, 11)],
    ("divide_by_10", "division", "division", (3, 4), divide_by_10, lambda p: p.operand_b in {10, 100} and p.operand_a % p.operand_b == 0 and p.operand_a <= (100 if p.band == 3 else 1000)),
    ("two_digit_divide", "division", "division", (4,), two_digit_divide, lambda p: p.operand_a <= 100 and p.operand_a % p.operand_b == 0 and p.correct_answer > 10),
    ("division_quotient", "division", "division", (4,), division_quotient, lambda p: p.correct_answer == p.operand_a // p.operand_b and p.operand_a < 100),
    ("remainder", "division", "remainder", (4,), remainder, lambda p: p.correct_answer == p.operand_a % p.operand_b < p.operand_b),
    ("compare", "comparison", "compare", (0, 1, 2, 3, 4), compare, lambda p: p.kind == "compare" and p.correct_answer in {-1, 0, 1} and max(p.operand_a, p.operand_b) <= (100 if p.band == 4 else 20)),
]

CATALOGUE: dict[str, Skill] = {code: Skill(code, topic, operation, bands, sample, check) for code, topic, operation, bands, sample, check in RAW}
TOPICS = ("addition", "subtraction", "counting", "multiplication", "division", "comparison")


def generate(code: str, session_id: UUID, ordinal: int, band: int) -> GeneratedProblem:
    """Deterministic for (session, ordinal, skill, band) so a retried generation yields the same task."""
    skill = CATALOGUE[code]
    if band not in skill.bands:
        raise ValueError(f"{code} does not support band {band}")
    rng = random.Random(f"{session_id}:{ordinal}:{code}:{band}")
    problem = skill.sample(rng, band)
    return GeneratedProblem(skill=code, band=band, operation=problem.operation, operand_a=problem.operand_a, operand_b=problem.operand_b, correct_answer=problem.correct_answer, kind=problem.kind, prompt=problem.prompt)


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
