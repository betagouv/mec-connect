#!/bin/bash

python -m celery -A mec_connect.worker worker -l INFO --concurrency=2
