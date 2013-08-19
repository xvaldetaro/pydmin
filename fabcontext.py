context = {}

# project changeable values
context['proj'] = "mendigames"
proj = context['proj']
context['github_username'] = "xvaldetaro"
context['github_email'] = "xvaldetaro@gmail.com"
context['git_url'] = "git@github.com:%s/%s.git" % (context['github_username'], proj)
context['domains'] = ["www.%s.com.br" % proj,"%s.com.br" % proj, "www.%s.com" % proj,"%s.com" % proj]
context['proxy_port'] = "8000"

# Development machine configs
context['dev_proj_dir'] = '/home/xande/apps/%s' % proj
context['dev_ssh_dir'] = '/home/xande/.ssh'
context['ssh_pem'] = "%s/key.pem" % context['dev_ssh_dir']
context['ssh_github_priv_key'] = "%s/github" % context['dev_ssh_dir']
context['dev_env_file'] = '/home/xande/confs/%s/prod.sh' % proj

# Remote machine changeable values
context['user'] = "xande"
context['hosts'] = ["54.232.198.136"]

# DB access
context['db_endpoint'] = 'localhost'
context['db_port'] = '3306'
context['db_root'] = 'root'
# This is NOT the root password (which you will type when prompted). 
# This is the desired project user db password.
context['db_password'] = '1234'

#uncomment to provide ssl:
#context['ssl_port'] = "8443"

# machine fixed values
context['home_dir'] = "/home/%s" % context['user']
base_dir = context['home_dir']
context['apps_dir'] = "%s/apps" % base_dir
context['venvs_dir'] = "%s/venvs" % base_dir
context['confs_dir'] = "%s/confs" % base_dir
context['logs_dir'] = "%s/logs" % base_dir
context['statics_dir'] = "%s/statics" % base_dir

# project fixed values
context['proj_app_dir'] = "%s/%s" % (context['apps_dir'],context['proj'])
context['proj_venv_dir'] = "%s/%s" % (context['venvs_dir'],context['proj'])
context['proj_conf_dir'] = "%s/%s" % (context['confs_dir'],context['proj'])
context['proj_log_dir'] = "%s/%s" % (context['logs_dir'],context['proj'])
context['ssh_dir'] = "/home/%s/.ssh" % context['user']
# uncomment to provide local statics
context['proj_static_dir'] = "%s/%s" % (context['statics_dir'],context['proj'])

context['launch_cmd'] = "%s/launch.sh" % context['proj_app_dir']