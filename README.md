# Pydmin

Pydmin is an collection of fabric commands for configuring a remote ubuntu server with everything necessary to power a nginx+gunicorn django server.

## Installation
pydmin depends on [fabric](https://github.com/fabric/fabric) and [jinja2](http://jinja.pocoo.org/docs/), so first you need to install them.

```
> pip install fabric jinja2
```

Then, clone this repository and open it in terminal.

## Components
The pydmin folder consists of 2 python files and a folder with templates. The python files are fabfile.py and fabcontext.py

**fabcontext.py** is where the module's commands pull system and project configuration parameters from. Therefore, we need to edit this file and put our own system and project data.

**fabfile.py** is the default fabric file, which is searched for commands when we execute ```> fab```, thus it has all of the modules usable commands. Ideally you should not need to edit this file.

**templates/** is where the fab commands will pull all the unix and python config files from. These files will be put into the server for executing taks such as launching and configuring gunicorn, nginx and upstart.

## Commands
The commands belong to 3 groups **system**, **project** and **deploy**.

**System** commands install nginx, python etc... and configures global stuff like /etc/nginx/nginx.conf

**Project** commands clones the repository, creates nginx and upstart entries, put launch scripts...

**Deploy** commands pull changes, update env files and restart services

## Usage
```
$ cd /path/to/pydmin
$ fab 
> Lists all the available commands
$ fab command
```
