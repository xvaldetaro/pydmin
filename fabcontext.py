context = {}

# machine changeable values
context['localuser'] = "xande"
context['user'] = "xande"
context['hosts'] = ["192.168.0.117"]
context['github_username'] = "xvaldetaro"
context['github_email'] = "xvaldetaro@gmail.com"
context['github_key'] = "github"

# project changeable values
context['proj'] = "toto"
proj = context['proj']
context['git_url'] = "git@github.com:xvaldetaro/%s.git" % proj
context['domains'] = ["www.%s.com.br" % proj,"%s.com.br" % proj, "www.%s.com" % proj,"%s.com" % proj]
context['proxy_port'] = "8000"
context['local_env_file'] = '/home/%s/confs/%s/prod.sh' % (context['localuser'], context['proj'])

# DB access
context['db_endpoint'] = 'localhost'
context['db_root'] = 'root'
# This is NOT the root password (which you will type when prompted). 
# This is the desired project user db password.
context['db_password'] = '1235'

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
context['local_ssh_dir'] = "/home/%s/.ssh" % context['localuser']
context['local_ssh_pem'] = "/home/%s/.ssh/key.pem" % context['localuser']
context['local_ssh_pub'] = "/home/%s/.ssh/id_rsa.pub" % context['localuser']
context['local_ssh_priv'] = "/home/%s/.ssh/id_rsa" % context['localuser']
# uncomment to provide local statics
# context['proj_static_dir'] = "%s/%s" % (context['statics_dir'],context['proj'])

context['launch_cmd'] = "%s/launch.sh" % context['proj_app_dir']