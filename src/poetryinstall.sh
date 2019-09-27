#!/bin/bash
if [[ "${ENV_TYPE}" == "PROD" ]]
then
    echo "$0: poetry install --no-dev"
    poetry install --no-dev
else
    echo "$0: poetry install"
    poetry install
fi