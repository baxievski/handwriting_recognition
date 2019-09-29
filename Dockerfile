FROM python:3.7

RUN pip install poetry
RUN poetry config settings.virtualenvs.create false
WORKDIR /code
COPY pyproject.toml poetry.lock ./src/poetryinstall.sh /code/
RUN chmod +x /code/poetryinstall.sh
ARG ENV_TYPE
RUN /code/poetryinstall.sh

RUN groupadd appuser && useradd appuser -g appuser -u 1000 
RUN mkdir /home/appuser
RUN chown appuser:appuser /home/appuser -R
RUN chown appuser:appuser /code -R
COPY ./src /code
USER appuser

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1
