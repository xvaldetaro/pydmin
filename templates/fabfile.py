from fabric.api import *

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

env.user = '{{ user }}'
env.key_filename = '{{ ssh_pem }}'
env.hosts = {{ hosts }}

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
    #s_aws_ssh_auth()
    s_folders()
    s_aptpkgs()
    s_pypkgs()
    s_envs()
    s_git()

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
    _apt("build-essential", "python-dev", "mysql-client", "python-mysqldb", "nginx", "memcached", "git",
      "python-setuptools", "python-pip", "libmysqlclient-dev")
 
    with settings(warn_only=True):
        _mkdir(r"{{ logs_dir }}/nginx")

    _put_template('nginx.conf', '/etc/nginx/nginx.conf')

    _put_template('upstart_nginx.conf', '/etc/init/nginx.conf')

def s_pypkgs():
    """
    Install the conf system pip packages. configure venvwrapper
    """
    _pip("virtualenv", "virtualenvwrapper")
    run("echo 'export WORKON_HOME={{ venvs_dir }}' >> /home/{{ user }}/.profile")
    run("echo 'source /usr/local/bin/virtualenvwrapper.sh' >> /home/{{ user }}/.profile")
    run("source /home/{{ user }}/.profile")
    
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
    put("{{ dev_ssh_dir }}/{{ ssh_github_priv_key }}", "{{ ssh_dir }}/id_rsa")
    run("chmod 600 {{ ssh_dir }}/id_rsa")
    run("git config --global user.name '{{ git_username }}'")
    run("git config --global user.email '{{ git_email }}'")
    run("ssh-keyscan github.com >> {{ ssh_dir }}/known_hosts")

# Project level commands
def project():
    """
    Executes all project commands in the proper order
    """
    p_folders()
    p_nginx()
    p_gunicorn()
    p_repo()
    p_venv()
    p_scripts()
    p_createdb_mysql()
    
def p_folders():
    """
    Creates the relevant project folders
    """
    _mkdir('{{ proj_venv_dir }}', 
        '{{ proj_conf_dir }}', '{{ proj_log_dir }}', '{{ proj_static_dir }}')
    {% if proj_static_dir %}
    _mkdir('{{ proj_static_dir }}')
    {% endif %}

def p_nginx():
    """
    Sets project's proxy nginx conf file and reloads nginx
    """
    _put_template('nginx_site.conf', '/etc/nginx/sites-available/{{ proj }}')
    _sudo("ln -f -s /etc/nginx/sites-available/{{ proj }} /etc/nginx/sites-enabled/{{ proj }}")
    with settings(warn_only=True):
        _sudo("initctl start nginx")
    _sudo("nginx -s reload")

def p_repo():
    """
    Clones git repository, creates venv and put launch templates
    """
    run("rm -rf {{ proj_app_dir }}")
    with cd('{{ apps_dir }}'):
        with settings(warn_only=True):
            run("git clone {{ git_url }}")
    
def p_venv():
    run("virtualenv --distribute {{proj_venv_dir}}")

def p_scripts():
    _put_template('gunicorn_conf.py', '{{proj_conf_dir}}/gunicorn_conf.py')
    _put_template('launch.sh', '{{proj_app_dir}}/launch.sh')

    run('chmod 700 {{proj_app_dir}}/launch.sh')

def p_gunicorn():
    """
    put gunicorn upstart conf
    """
    _put_template('upstart_process.conf', '/etc/init/{{ proj }}.conf')

def p_createdb_mysql():
    """
    Create user (name of project) and database (also name of project) with proper priviledges;
    """
    _put_template_('createdb_mysql', '{{proj_conf_dir}}/createdb_mysql')
    with settings(warn_only=True):
        run('mysql -u {{db_root}} -h {{db_endpoint}} -P {{db_port}} -p mysql < {{proj_conf_dir}}/createdb_mysql')
        run('rm {{proj_conf_dir}}/createdb_mysql')

def p_dropdb_mysql():
    """
    Create user (name of project) and database (also name of project) with proper priviledges;
    """
    _put_template_('dropdb_mysql', '{{proj_conf_dir}}/dropdb_mysql')
    with settings(warn_only=True):
        run('mysql -u {{db_root}} -h {{db_endpoint}} -P {{db_port}} -p mysql < {{proj_conf_dir}}/dropdb_mysql')
        run('rm {{proj_conf_dir}}/dropdb_mysql')

# Deploying commands
def deploy():
    """
    Executes all deploy commands in proper order.
    """
    d_putenv()
    d_pull()
    d_syncdb()
    d_restart()

def d_pull():
    """
    Pull changes to repo, install pip requirements and tries to collect static
    """
    with cd('{{ proj_app_dir }}'):
        run("git pull")

        _virtualenv_command('pip install -r {{proj_app_dir}}/requirements.txt')
        {% if proj_static_dir %}
        _fullenv_command('python manage.py collectstatic')
        {% endif %}

def d_putenv():
    """
    Put the environment file
    """
    put('{{local_env_file}}', '{{proj_conf_dir}}/env.sh')
    run('chmod 600 {{proj_conf_dir}}/env.sh')

def d_syncdb():
    """
    Executes django's syncdb
    """
    with cd('{{ proj_app_dir }}'):
        _fullenv_command('python manage.py syncdb')

def d_collectstatic():
    """
    Executes django's syncdb
    """
    with cd('{{ proj_app_dir }}'):
        _fullenv_command('python manage.py collectstatic')

def d_restart():
    """
    Restarts gunicorn service
    """
    with settings(warn_only=True):
        _sudo("initctl stop {{proj}}")
        _sudo("initctl start {{proj}}")


# Log commands
def l_e():
    """
    Prints error log
    """
    run("cat {{proj_log_dir}}/error.log")

def l_a():
    """
    Prints access log
    """
    run("cat {{proj_log_dir}}/access.log")

def l_ne():
    """
    Prints ningx error log
    """
    run("cat {{proj_log_dir}}/nginx_error.txt")

def l_na():
    """
    Prints nginx access log
    """
    run("cat {{proj_log_dir}}/nginx_access.txt")

### Internal commands
def _mkdir(*dirs):
    for dire in dirs:
        with settings(warn_only=True):
            _sudo("mkdir -p %s" % dire)

def _apt(*pkgs):
    """
    Runs apt-get install commands
    """
    for pkg in pkgs:
        _sudo("apt-get install -qq %s" % pkg)

def _env(var, value):
    run("echo 'export %s=%s' >> /home/{{ user }}/.profile" % (var, value))
    run("source /home/{{ user }}/.profile")

def _pip(*pkgs):
    """
    Runs pip install commands
    """
    for pkg in pkgs:
        _sudo("pip install %s" % pkg)

def _put_template(template_name, destination):
    f = open(THIS_DIR+'/'+template_name, 'r')
    with settings(warn_only=True):
        _sudo("rm %s" % destination)
        _sudo("echo '%s' >> %s" % (f.read(), destination))

def _sudo(cmd_text):
    """
    Run command as root
    """
    ssh_pem = '{{ ssh_pem }}'
    with settings(key_filename=ssh_pem):
        sudo(cmd_text)

def _fullenv_command(command):
    with prefix('source {{ proj_conf_dir }}/env.sh'):
        _virtualenv_command(command)

def _virtualenv_command(command):
    """
    Activates virtualenv and runs command
    """
    run("source {{proj_venv_dir}}/bin/activate && %s" % command)
    