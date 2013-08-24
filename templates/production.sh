export "ALLOWED_HOSTS=127.0.0.1"
export "DATABASE_URL={{db}}://{{proj}}:{{db_password}}@{{db_endpoint}}:{{db_port}}/{{proj}}"
export "SECRET_KEY={{secret_key}}"

export "APPS_DIR=/home/xande/apps"
{% if proj_static_dir %}export "STATIC_ROOT=/home/xande/statics/mendigames"{% endif %}
export "ENV=production"
