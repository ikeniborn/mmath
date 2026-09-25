"""Pre/post selection constraints: which skills and bands a session may use, and how actions move bands."""

from mental_math.game.catalogue import CATALOGUE, eligible_pairs


def band_bounds(code: str) -> tuple[int, int]:
    bands = CATALOGUE[code].bands
    return bands[0], bands[-1]


def step_band(code: str, band: int, action: str) -> int:
    """Move one supported band at most; 'repeat', 'hint' and 'switch' keep it."""
    bands = CATALOGUE[code].bands
    index = bands.index(band)
    if action == "harder" and index + 1 < len(bands):
        return bands[index + 1]
    if action == "easier" and index > 0:
        return bands[index - 1]
    return band


def interleaved(pairs: list[tuple[str, int]], topics: list[str]) -> list[tuple[str, int]]:
    """Order eligible pairs so enabled topics alternate: first skill of each topic, then the second of each, and so on."""
    by_topic = {topic: [pair for pair in pairs if CATALOGUE[pair[0]].topic == topic] for topic in topics}
    result = []
    while any(by_topic.values()):
        for topic in topics:
            if by_topic[topic]:
                result.append(by_topic[topic].pop(0))
    return result


def next_skill(settings: dict, automatic_bands: dict[str, int], current: str | None, action: str) -> tuple[str, int]:
    """Keep the current skill unless the applied action is 'switch', which moves to the next eligible skill."""
    pairs = interleaved(eligible_pairs(settings["topics"], settings["mode"], settings["difficulty_band"], automatic_bands), settings["topics"])
    if not pairs:
        raise ValueError("no eligible skill for the session settings")
    codes = [code for code, _ in pairs]
    if current is None or current not in codes:
        return pairs[0]
    index = codes.index(current)
    if action == "switch" and len(pairs) > 1:
        index = (index + 1) % len(pairs)
    return pairs[index]
