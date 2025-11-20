FROM python:3.12-slim

ENV POETRY_VIRTUALENVS_CREATE=false \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir poetry==1.8.2

COPY pyproject.toml ./
RUN poetry install --no-root --no-interaction --no-ansi

COPY src ./src
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini

CMD ["uvicorn", "sytefy_backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
