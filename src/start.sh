#!/usr/bin/env bash

if [[ $ENV == "PRODUCTION" ]]
then
    python /code/manage.py collectstatic --no-input
    uwsgi --ini /code/uwsgi.ini
else
    python /code/manage.py runserver 0.0.0.0:8000
fi