from jinja2 import Template, Environment, FileSystemLoader
from fabcontext import context
import os, os.path

# Capture our current directory
THIS_DIR = os.path.dirname(os.path.abspath(__file__))

jenv = Environment(loader=FileSystemLoader(THIS_DIR+'/templates'))

def render_to_file(template_name):
    tp = jenv.get_template(template_name)
    f =  open('%s/fabtemplates/%s' % (context['dev_proj_dir'], template_name), 'w')
    f.write(tp.render(context))
    f.close()

def droptemplates():
    try:
        os.makedirs("%s/fabtemplates" % context['dev_proj_dir'])
    except:
        pass
    for root, _, files in os.walk(THIS_DIR+'/templates'):
        for f in files:
            render_to_file(f)

droptemplates()