import os

bind = "127.0.0.1:{{ proxy_port }}"
workers = (os.sysconf("SC_NPROCESSORS_ONLN") * 2) + 1
loglevel = "error"
accesslog = "{{ proj_log_dir }}/access.log"
errorlog = "{{ proj_log_dir }}/error.log"
proc_name = "{{ proj }}"