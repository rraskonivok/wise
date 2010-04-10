#!/bin/bash

SAGE_PATH='/opt/sage'
ADDRESS='localhost'
PORT=8100

echo $SAGE_PATH

$SAGE_PATH/bin/sage -python manage.py run_gunicorn $ADDRESS:$PORT
