#!/bin/bash
source {{proj_venv_dir}}/bin/activate
source {{ proj_conf_dir }}/env.sh
export PYTHONPATH={{proj_app_dir}}:$PYTHONPATH
gunicorn -c {{ proj_conf_dir }}/gunicorn_conf.py {{ proj }}.wsgi:application
