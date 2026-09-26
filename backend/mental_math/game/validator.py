def grade(problem, answer: int) -> bool:
    """Deterministic grading against the server-only correct answer."""
    return int(answer) == int(problem.correct_answer)
