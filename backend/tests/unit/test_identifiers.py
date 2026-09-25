from mental_math.accounts.models import Account, AuthSession, LoginFailure
from mental_math.game.models import Attempt, LearningSession, PolicyDecision, Problem
from mental_math.players.models import Player


def test_every_generated_primary_key_is_time_ordered_uuid7():
    for model in (Account, LoginFailure, Player, LearningSession, Problem, Attempt, PolicyDecision):
        default = model.__table__.c.id.default
        first, second = default.arg(None), default.arg(None)
        assert first.version == second.version == 7, model.__tablename__
        assert first < second, model.__tablename__
    assert AuthSession.__table__.c.token_hash.default is None
