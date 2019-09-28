FROM python:3.7

RUN pip install poetry
RUN poetry config settings.virtualenvs.create false
WORKDIR /code
COPY pyproject.toml poetry.lock ./src/poetryinstall.sh /code/
RUN chmod +x /code/poetryinstall.sh
ARG ENV_TYPE
RUN /code/poetryinstall.sh

RUN groupadd -g 1000 appuser && useradd -r -u 999 -g appuser appuser
RUN mkdir /home/appuser
RUN chown appuser:appuser /home/appuser -R
COPY ./src /code
RUN chown appuser:appuser /code -R
USER appuser

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1
