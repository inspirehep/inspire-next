# -*- coding: utf-8 -*-

"""Deployment of INSPIRE Labs."""

import json

from fabric.api import *
from fabric.utils import error
from fabric.contrib.files import exists

env.directory = '/opt'  # remote directory
env.hosts = ['inspirevm11']  # list of servers


@task
def pack():
    """Create a new source distribution as tarball."""
    with open(".bowerrc") as fp:
        bower = json.load(fp)

    local("inveniomanage assets build --directory {directory}/gen"
          .format(**bower))
    return local("python setup.py sdist --formats=gztar", capture=False) \
        .succeeded


@task
def create_virtualenv():
    """Create the virtualenv."""
    package = local("python setup.py --fullname", capture=True).strip()

    with cd(env.directory):
        if exists(package):
            return error("This version {0} is already installed."
                         .format(package))

        with settings(sudo_user="invenio"):
            return sudo("virtualenv {0}".format(package)).succeeded


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
            success = sudo("{0}/bin/python setup.py install".format(venv))

            if success:
                # post install
                sudo("{0}/bin/inveniomanage collect".format(venv))
            return success
