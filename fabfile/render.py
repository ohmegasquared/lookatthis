#!/usr/bin/env python

"""
Commands for rendering various parts of the app stack.
"""

from glob import glob
import os

from fabric.api import local, require, task
from fabric.state import env

import app
import app_config

@task
def less():
    """
    Render LESS files to CSS.
    """
    for path in glob('%s/less/*.less' % env.static_path):
        filename = os.path.split(path)[-1]
        name = os.path.splitext(filename)[0]
        out_path = '%s/www/css/%s.less.css' % (env.static_path, name)

        try:
            local('node_modules/less/bin/lessc %s %s' % (path, out_path))
        except:
            print 'It looks like "lessc" isn\'t installed. Try running: "npm install"'
            raise

@task
def app_config_js():
    """
    Render app_config.js to file.
    """
    from static_post import _app_config_js

    response = _app_config_js(env.slug)
    js = response[0]

    with open('%s/www/js/app_config.js' % env.static_path, 'w') as f:
        f.write(js)

@task
def copytext_js(slug):
    """
    Render COPY to copy.js.
    """
    from static import copy_js

    response = copy_js(slug)
    js = response[0]

    with open('%s/www/js/copy.js' % env.static_path, 'w') as f:
        f.write(js)

@task(default=True)
def render_all():
    """
    Render HTML templates and compile assets.
    """
    from flask import g

    require('slug', provided_by=['post'])

    less()
    app_config_js()
    copytext_js(env.slug)

    compiled_includes = {}

    app_config.configure_targets(env.get('settings', None))

    with app.app.test_request_context():
        path = 'posts/%s/www/index.html' % env.slug

    with app.app.test_request_context(path=env.static_path):
        print 'Rendering %s' % path

        g.compile_includes = True
        g.compiled_includes = compiled_includes

        view = app.__dict__['_post']
        content = view(env.slug)

    with open(path, 'w') as f:
        f.write(content.encode('utf-8'))

