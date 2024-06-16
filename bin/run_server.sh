#!/bin/bash

gunicorn --timeout 300 mec_connect.wsgi:application --log-file -
