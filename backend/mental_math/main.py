from fastapi import FastAPI, Request

from mental_math.accounts.routes import router as accounts_router
from mental_math.config import Settings
from mental_math.db import session_factory
from mental_math.game.routes import router as game_router
from mental_math.players.routes import router as players_router


def create_app() -> FastAPI:
    settings = Settings.from_env()
    app = FastAPI(title="Mental Math API", version="0.1.0")
    app.state.settings = settings
    app.state.session_factory = session_factory(settings.database_url)
    app.include_router(accounts_router)
    app.include_router(players_router)
    app.include_router(game_router)

    @app.middleware("http")
    async def no_store(request: Request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    return app
