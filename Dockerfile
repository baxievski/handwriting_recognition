FROM python:3.8.0

ARG ENV_TYPE

ENV ENV_TYPE=${ENV_TYPE} \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VERSION=1.0.0b9

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /code

COPY pyproject.toml poetry.lock /code/

RUN poetry install $(test "$ENV_TYPE"=="PROD" && echo "--no-dev") \
    --no-interaction \
    --no-ansi

RUN groupadd appuser;\
    useradd appuser -g appuser -u 1000; \
    mkdir /home/appuser; \
    chown appuser:appuser /home/appuser -R; \
    chown appuser:appuser /code -R

COPY ./src /code

USER appuser
