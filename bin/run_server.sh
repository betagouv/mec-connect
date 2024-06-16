#!/bin/bash

gunicorn --timeout 300 --chdir core mec_connect.wsgi --log-file -
