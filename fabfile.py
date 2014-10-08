# -*- coding: utf-8 -*-

"""Deployment of INSPIRE Labs."""

import json

from fabric.api import *
from fabric.utils import error
from fabric.contrib.files import exists

env.directory = '/opt'  # remote directory

env.roledefs = {
    'dev01': ['inspirevm08.cern.ch'],
    'dev02': ['inspirevm11.cern.ch'],
}


@task
def vm08():
    """
    Activate configuration for INSPIRE DEV server.
    """
    env.roles = ['dev01']


@task
def vm11():
    """
    Activate configuration for INSPIRE DEV server.
    """
    env.roles = ['dev02']


@task
def pack():
    """Create a new source distribution as tarball."""
    local("inveniomanage assets build --directory {0}"
          .format("inspire/base/static/gen"))
    return local("python setup.py sdist --formats=gztar", capture=False) \
        .succeeded


@task
def create_virtualenv():
    """Create the virtualenv."""
    package = local("python setup.py --fullname", capture=True).strip()
    pythonpath = "/opt/rh/python27/root/usr/bin/python"
    with cd(env.directory):
        if exists(package):
            return error("This version {0} is already installed."
                         .format(package))

        with settings(sudo_user="invenio"):
            return sudo("virtualenv {0} --python={1}".format(package, pythonpath)).succeeded


@task
def install():
    """Install package."""
    package = local("python setup.py --fullname", capture=True).strip()
    venv = "{0}/{1}".format(env.directory, package)

    if not exists(venv):
        return error("Meh? I need a virtualenv first.")

    # Upload the package and put it into our virtualenv.
    put("dist/{0}.tar.gz".format(package), "/tmp/app.tgz")
    with settings(sudo_user="invenio"):
        sudo("mkdir -p {0}/src".format(venv))
        with cd("{0}/src".format(venv)):
            sudo("tar xzf /tmp/app.tgz")
            run("rm -rf /tmp/app.tgz")

        # Jump into the virtualenv and install stuff
        with cd("{0}/src/{1}".format(venv, package)):
            with prefix('source {0}/bin/activate'.format(venv)):
                sudo("pip install Babel")
                sudo("pip install numpy")
                sudo("pip install git+git://github.com/mrjoes/flask-admin.git#egg=Flask-Admin-1.0.9.dev0")
                success = sudo("python setup.py install")

                if success:
                    # INSPIRE specific configuration
                    sudo("pip install /afs/cern.ch/project/inspire/repo/inspireconf-dev.tar.gz --upgrade")
                    # post install
                    sudo("inveniomanage collect")
                    # Set Flask Host configuration
                    sudo("inveniomanage config set CFG_SITE_URL {0}".format(env.host_string))
                    sudo("inveniomanage config set CFG_SITE_SECURE_URL {0}".format(env.host_string))
                    # Create Apache configuration
                    sudo("inveniomanage apache create-config")
                    sudo("ln -s {0} /opt/invenio".format(venv))
                return success
