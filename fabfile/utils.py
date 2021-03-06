#!/usr/bin/env python

"""
Utilities used by multiple commands.
"""

from glob import glob
import re

from fabric.api import local, prompt
from fabric.state import env

import app_config


def confirm(message):
    """
    Verify a users intentions.
    """
    answer = prompt(message, default="Not at all")

    if answer.lower() not in ('y', 'yes', 'buzz off', 'screw you'):
        exit()

def _gzip(in_path='www', out_path='.gzip'):
    """
    Gzips everything in www and puts it all in gzip
    """
    local('python gzip_assets.py %s %s' % (in_path, out_path))

def _deploy_to_s3(path='.gzip'):
    """
    Deploy the gzipped stuff to S3.
    """
    # Clear files that should never be deployed
    local('rm -rf %s/live-data' % path)
    local('rm -rf %s/sitemap.xml' % path)

    exclude_flags = ''
    include_flags = ''

    with open('gzip_types.txt') as f:
        for line in f:
            exclude_flags += '--exclude "%s" ' % line.strip()
            include_flags += '--include "%s" ' % line.strip()

    exclude_flags += '--exclude "www/assets" '

    sync = 'aws s3 sync %s/ %s --acl "public-read" ' + exclude_flags + ' --cache-control "max-age=5" --region "us-east-1"'
    sync_gzip = 'aws s3 sync %s/ %s --acl "public-read" --content-encoding "gzip" --exclude "*" ' + include_flags + ' --cache-control "max-age=5" --region "us-east-1"'
    sync_assets = 'aws s3 sync %s/ %s --acl "public-read" --cache-control "max-age=86400" --region "us-east-1"'


    print path.split('.gzip/')[1]

    for bucket in app_config.S3_BUCKETS:
        if path.split('.gzip/')[1].startswith('tumblr'):
            local(sync % (path, 's3://%s/%s/%s' % (
                bucket,
                app_config.PROJECT_SLUG,
                path.split('.gzip/')[1]
            )))

        else:
            local(sync % (path, 's3://%s/%s/posts/%s' % (
                bucket,
                app_config.PROJECT_SLUG,
                env.post_config.DEPLOY_SLUG
            )))

        if path.split('.gzip/')[1].startswith('tumblr'):
            local(sync_gzip % (path, 's3://%s/%s/%s' % (
                bucket,
                app_config.PROJECT_SLUG,
                path.split('.gzip/')[1]
            )))

        else:
            local(sync_gzip % (path, 's3://%s/%s/posts/%s' % (
                bucket,
                app_config.PROJECT_SLUG,
                env.post_config.DEPLOY_SLUG
            )))


        if path.split('.gzip/')[1].startswith('tumblr'):
            local(sync_assets % ('%s/assets/' % path, 's3://%s/%s/posts/%s/assets/' % (
                bucket,
                app_config.PROJECT_SLUG,
                path.split('.gzip/')[1]
            )))

        else:
            local(sync_assets % ('%s/assets/' % path, 's3://%s/%s/posts/%s/assets/' % (
                bucket,
                app_config.PROJECT_SLUG,
                env.post_config.DEPLOY_SLUG
            )))

def _find_slugs(slug):
    posts = glob('%s/*' % app_config.POST_PATH)

    for folder in posts:
        folder_slug = folder.split('%s/' % app_config.POST_PATH)[1]

        if slug == folder_slug:
            return folder_slug

    return

def replace_in_file(filename, find, replace):
    with open(filename, 'r') as f:
        contents = f.read()

    contents = contents.replace(find, replace)

    with open(filename, 'w') as f:
        f.write(contents)
