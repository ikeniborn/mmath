from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware

from mental_math.accounts.routes import router as accounts_router
from mental_math.config import Settings
from mental_math.db import session_factory
from mental_math.game.routes import router as game_router
from mental_math.health import router as health_router
from mental_math.observability import configure_logging, metrics, request_metrics
from mental_math.players.routes import router as players_router


def create_app() -> FastAPI:
    settings = Settings.from_env()
    app = FastAPI(title="Mental Math API", version="0.1.0")
    app.state.settings = settings
    app.state.session_factory = session_factory(settings.database_url)
    app.state.logger = configure_logging()
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=list(settings.allowed_hosts))
    app.include_router(accounts_router)
    app.include_router(players_router)
    app.include_router(game_router)
    app.include_router(health_router)

    @app.get("/internal/metrics", include_in_schema=False)
    async def internal_metrics():
        return PlainTextResponse(metrics.render(), media_type="text/plain; version=0.0.4")

    app.middleware("http")(request_metrics)

    @app.middleware("http")
    async def no_store(request: Request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    return app
