FROM python:3.12-slim@sha256:a0f57064cbdcd6285fa45f51237ab0b35ea8ebaed06a1f5973e89e19dfb86704 AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir setuptools==80.9.0 wheel==0.45.1 \
    && pip install --no-cache-dir --no-build-isolation . \
    && useradd --create-home --uid 10001 researcher
COPY data ./data

FROM base AS test
ENV RUFF_CACHE_DIR=/tmp/ruff-cache PYTEST_ADDOPTS="-o cache_dir=/tmp/pytest-cache"
COPY requirements-ci.txt ./
RUN pip install --no-cache-dir -r requirements-ci.txt
COPY tests ./tests
COPY ci ./ci
USER 10001
CMD ["python", "-m", "pytest", "tests"]

FROM base AS runtime
USER 10001
ENTRYPOINT ["curriculum-graph"]
CMD ["data/sample_curriculum.json", "stats"]
