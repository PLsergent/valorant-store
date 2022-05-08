#!/bin/sh
poetry run gunicorn --bind 127.0.0.1:5000 app:app