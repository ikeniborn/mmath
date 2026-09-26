FROM python:3.12-slim@sha256:2f17fc044b579bab302c2e8054d3a686e2cb9a83de48e70534b94cd8ebbe06a9
WORKDIR /app
RUN pip install --no-cache-dir uv==0.8.13
COPY backend/pyproject.toml backend/uv.lock /app/backend/
RUN uv sync --project /app/backend --frozen --no-dev
COPY backend /app/backend
WORKDIR /app/backend
CMD ["/app/backend/.venv/bin/uvicorn", "mental_math.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
