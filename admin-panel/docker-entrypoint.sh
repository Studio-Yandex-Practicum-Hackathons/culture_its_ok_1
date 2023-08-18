#!/bin/bash

set -e

while ! nc -z postgres $POSTGRES_PORT; do
  echo "Waiting for postgres to start..."
  sleep 1
done
echo "Postgres started"

python manage.py migrate
python manage.py collectstatic --no-input

uwsgi --strict --ini uwsgi.ini