# syntax=docker/dockerfile:1

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN groupadd --system app && useradd --system --gid app --create-home app

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY data ./data

FROM base AS test
COPY tests ./tests
RUN python -m pip install --no-cache-dir -e ".[dev]"
CMD ["pytest", "-q"]

FROM base AS runtime
RUN python -m pip install --no-cache-dir .
RUN chown -R app:app /app
USER app
ENTRYPOINT ["curriculum-graph"]
CMD ["data/sample_curriculum.json", "stats"]
