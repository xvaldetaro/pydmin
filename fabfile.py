from fabcontext import context
from fabric.api import *
from jinja2 import Template, Environment, PackageLoader
from fabcontext import context

jenv = Environment(loader=PackageLoader('fabhelper', 'templates'))

env.user = context['user']
env.key_filename = context['local_ssh_priv']
env.hosts = context['hosts']

def all():
    """
    Execute all the system, project and deploy commands in the correct order
    """
    system()
    project()
    deploy()

### System level commands
def system():
    """
    Executes all system commands in the correct order
    """
    s_aws_ssh_auth()
    s_folders()
    s_aptpkgs()
    s_pypkgs()
    s_envs()
    s_git()

def s_aws_ssh_auth():
    """
    Connect as ubuntu using localuserhome/.ssh/key.pem .
    Transfer localuserhome/.ssh/id_rsa to temp remote folder
    creates actual_userremotehome/.ssh folder and chowns it
    cats copied id_rsa to actual_userremotehome/.ssh/authorized_keys and chowns it
    """
    local_ssh_pem = context['local_ssh_pem']
    with settings(user="ubuntu",key_filename=local_ssh_pem):
        _mkdir(r"{{ ssh_dir }}")
        _put("{{ local_ssh_pub }}", "/home/ubuntu/temp.k" )
        _sudo("cat /home/ubuntu/temp.k >> {{ ssh_dir }}/authorized_keys")
        _sudo("chown {{ user }} {{ ssh_dir }}/authorized_keys")
        _sudo("rm /home/ubuntu/temp.k")

def s_folders():
    """
    Creates the main folders (apps, venvs, confs, logs, statics)
    """
    _mkdir(r"{{ home_dir }}", r"{{ apps_dir }}", r"{{ venvs_dir }}", 
        r"{{ confs_dir }}", r"{{ logs_dir }}", r"{{ statics_dir }}" )

def s_aptpkgs():
    """
    Install apt-gets. Set up nginx.conf and create nginx logs dir.
    """
    _apt("mysql-client", "libmysqlclient-dev", "nginx", "memcached", "git",
      "python-setuptools", "python-dev", "build-essential", "python-pip", "python-mysqldb")
 
    with settings(warn_only=True):
        _mkdir(r"{{ logs_dir }}/nginx")

    _put_template('nginx.conf', context, '/etc/nginx/nginx.conf')

    _put_template('upstart_nginx.conf', context, '/etc/init/nginx.conf')

def s_pypkgs():
    """
    Install the conf system pip packages. configure venvwrapper
    """
    _pip("virtualenv", "virtualenvwrapper")
    _run("echo 'export WORKON_HOME={{ venvs_dir }}' >> /home/{{ user }}/.profile")
    _run("echo 'source /usr/local/bin/virtualenvwrapper.sh' >> /home/{{ user }}/.profile")
    _run("source /home/{{ user }}/.profile")
    
def s_envs():
    """
    Sets env vars for all the main folders (apps, venvs, confs, logs, statics)
    """
    _env('APPS_DIR', '{{ apps_dir }}')
    _env('VENVS_DIR', '{{ venvs_dir }}')
    _env('CONFS_DIR', '{{ confs_dir }}')
    _env('LOGS_DIR', '{{ logs_dir }}')
    _env('STATICS_DIR', '{{ statics_dir }}')

def s_git():
    """
    Sets git global user and email, put private key for cloning and authorize github known host
    """
    _put("{{ local_ssh_dir }}/{{ github_key }}", "{{ ssh_dir }}/id_rsa")
    _run("chmod 600 {{ ssh_dir }}/id_rsa")
    _run("git config --global user.name '{{ git_username }}'")
    _run("git config --global user.email '{{ git_email }}'")
    _run("ssh-keyscan github.com >> {{ ssh_dir }}/known_hosts")

# Project level commands
def project():
    """
    Executes all project commands in the proper order
    """
    p_folders()
    p_nginx()
    p_gunicorn()
    p_repo()
    
def p_folders():
    """
    Creates the relevant project folders
    """
    _mkdir('{{ proj_venv_dir }}', 
        '{{ proj_conf_dir }}', '{{ proj_log_dir }}' )
    
    if 'proj_static_dir' in context:
        _mkdir('{{ proj_static_dir }}')

def p_nginx():
    """
    Sets project's proxy nginx conf file and reloads nginx
    """
    _put_template('nginx_site.conf', context, '/etc/nginx/sites-available/{{ proj }}')
    _sudo("ln -f -s /etc/nginx/sites-available/{{ proj }} /etc/nginx/sites-enabled/{{ proj }}")
    with settings(warn_only=True):
        _sudo("initctl start nginx")
    _sudo("nginx -s reload")

def p_repo():
    """
    Clones git repository, creates venv and put launch templates
    """
    with cd(context['apps_dir']):
        with settings(warn_only=True):
            _run("git clone {{ git_url }}")
    
    _run("virtualenv --distribute {{proj_venv_dir}}")
    _put_template_('gunicorn_conf.py', context, '{{proj_conf_dir}}/gunicorn_conf.py')
    _put_template_('launch.sh', context, '{{proj_app_dir}}/launch.sh')

    _run('chmod 700 {{proj_app_dir}}/launch.sh')


def p_gunicorn():
    """
    put gunicorn upstart conf
    """
    _put_template('upstart_process.conf', context, '/etc/init/{{ proj }}.conf')

# Deploying commands
def deploy():
    """
    Executes all deploy commands in proper order.
    """
    d_putenv()
    d_pull()
    #d_syncdb()
    d_restart()

def d_pull():
    """
    Pull changes to repo, install pip requirements and tries to collect static
    """
    with cd(context['proj_app_dir']):
        _run("git pull")

        _virtualenv_command('pip install -r {{proj_app_dir}}/requirements.txt')
        if 'proj_static_dir' in context:
            _fullenv_command('python manage.py collectstatic')

def d_putenv():
    """
    Put the environment file
    """
    _put('{{local_env_file}}', '{{proj_conf_dir}}/env.sh')
    _run('chmod 600 {{proj_conf_dir}}/env.sh')

def d_syncdb():
    """
    Executes django's syncdb
    """
    with cd('{{proj_app_dir}}'):
        _fullenv_command('python manage.py syncdb')

def d_restart():
    """
    Restarts gunicorn service
    """
    with settings(warn_only=True):
        _sudo("initctl stop {{proj}}")
        _sudo("initctl start {{proj}}")

### Internal commands
def _mkdir(*dirs):
    for dire in dirs:
        with settings(warn_only=True):
            _sudo("mkdir -p %s" % dire)
        _sudo("chown %s %s" % (context['user'], dire) )

def _apt(*pkgs):
    """
    Runs apt-get install commands
    """
    for pkg in pkgs:
        _sudo("apt-get install -qq %s" % pkg)

def _env(var, value):
    _run("echo 'export %s=%s' >> /home/{{ user }}/.profile" % (var, value))
    _run("source /home/{{ user }}/.profile")

def _pip(*pkgs):
    """
    Runs pip install commands
    """
    for pkg in pkgs:
        _sudo("pip install %s" % pkg)

def _run(cmd_text):
    """
    Runs command with active user
    """
    command = _render(cmd_text)
    run(command)

def _put_template_(template_name, context, destination):
    tp = jenv.get_template(template_name)
    with settings(warn_only=True):
        _run("rm %s" % destination)
        _run("echo '%s' >> %s" % (tp.render(context), destination))

def _put_template(template_name, context, destination):
    tp = jenv.get_template(template_name)
    with settings(warn_only=True):
        _sudo("rm %s" % destination)
        _sudo("echo '%s' >> %s" % (tp.render(context), destination))

def _sudo(cmd_text):
    """
    Run command as root
    """
    command = _render(cmd_text)
    sudo(command)

def _render(template):
    """
    Does variable replacement
    """
    return Template(template).render(context)

def _put(file, destination):
    """
    Moves a file from local computer to server
    """
    put(_render(file), _render(destination))

def _fullenv_command(command):
    with prefix('source %s/env.sh' % context['proj_conf_dir']):
        _virtualenv_command(command)

def _virtualenv_command(command):
    """
    Activates virtualenv and runs command
    """
    _run("source {{proj_venv_dir}}/bin/activate && %s" % command)