# Dockerfile used to containerise the app in the CI pipeline.
#
# (c) 2024 Alberto Morón Hernández
FROM python:3.12-slim

WORKDIR /app

COPY requirements/base.txt requirements/base.txt

RUN pip install uv
RUN uv pip install --system --no-cache-dir -r requirements/base.txt

COPY . .
# actual .env is listed in .dockerignore. Create empty file so it can be overridden
# with `--env .env` when calling `docker run`.
RUN touch .env

CMD ["uvicorn", "depositduck.main:webapp", "--host", "0.0.0.0", "--port", "80"]
