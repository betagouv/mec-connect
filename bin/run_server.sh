#!/bin/bash

if [ "$1" = "dev" ]
then
    python manage.py runserver 0.0.0.0:8002
else
    gunicorn --timeout 300 mec_connect.wsgi:application --log-file -
fi
