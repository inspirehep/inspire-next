# -*- coding: utf-8 -*-

"""Deployment of INSPIRE Labs."""

import json

from fabric.api import *
from fabric.utils import error
from fabric.contrib.files import exists

env.directory = '/opt'  # remote directory
env.conf_directory = "/afs/cern.ch/project/inspire/repo/inspire-configuration.git"

env.roledefs = {
    'prod': ['inspirelabsvm01'],
    'dev01': ['inspirevm08.cern.ch'],
    'dev02': ['inspirevm11.cern.ch'],
}


@task
def prod():
    """Activate configuration for INSPIRE PROD server."""
    env.roles = ['prod']
    env.site_url = "http://inspirelabsvm01.cern.ch"
    env.site_secure_url = "https://inspirelabsvm01.cern.ch"
    env.conf_branch = "prod"


@task
def vm08():
    """Activate configuration for INSPIRE DEV server."""
    env.roles = ['dev01']
    env.site_url = "http://inspirelabstest.cern.ch"
    env.site_secure_url = "https://inspirelabstest.cern.ch"


@task
def vm11():
    """Activate configuration for INSPIRE DEV server."""
    env.roles = ['dev02']
    env.site_url = "http://inspirevm11.cern.ch"
    env.site_secure_url = "https://inspirevm11.cern.ch"


@task
def pack():
    """Create a new source distribution as tarball."""
    with open(".bowerrc") as fp:
        bower = json.load(fp)

    choice = prompt("Clean and reinstall local assets? (y/N)", default="no")
    if choice.lower() in ["y", "ye", "yes"]:
        clean_assets()

    local("inveniomanage assets build --directory {directory}/../gen"
          .format(**bower))
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

    success = 1

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
                    path_to_invenio = sudo("python -c 'import invenio; print invenio.__path__[0]'")
                    if path_to_invenio:
                        sudo("pybabel compile -d {0}/base/translations".format(path_to_invenio.strip()))
                    # INSPIRE specific configuration
                    with cd(env.conf_directory):
                        config_location = "/tmp/inspire-configuration"
                        sudo("mkdir -p {0}".format(config_location))
                        sudo("GIT_WORK_TREE={0} git checkout -f {1}".format(config_location, env.conf_branch))
                        sudo("pip install {0} --upgrade".format(config_location))
                    # post install
                    sudo("inveniomanage collect")
                    with warn_only():
                        # Compile base Invenio translatation to avoid translation error
                        prefix_folder = sudo('python -c "import invenio; print(invenio.__path__[0])"')
                        prefix_folder = prefix_folder.split("\n")
                        sudo("pybabel compile -fd {0}/base/translations".format(prefix_folder[-1]))
                        # Set Flask Host configuration
                        sudo("inveniomanage config set CFG_SITE_URL {0}".format(env.site_url))
                        sudo("inveniomanage config set CFG_SITE_SECURE_URL {0}".format(env.site_secure_url))
                        # Create Apache configuration
                        sudo("inveniomanage apache create-config")
                        sudo("rm /opt/invenio")
                        sudo("ln -s {0} /opt/invenio".format(venv))

        with cd("{0}/var".format(venv)):
            sudo("mkdir -p log/bibsched")
            sudo("chown -R invenio.invenio log/bibsched")

    if success:
        sudo("supervisorctl restart celeryd")
    return success


@task
def restart_celery():
    """Restart celery workers."""
    return sudo("supervisorctl restart celeryd")


@task
def restart_apache():
    """Restart celery workers."""
    return sudo("service httpd restart")


@task
def clean_assets():
    """Helper to ensure all assets are up to date."""
    local("rm -rf $VIRTUAL_ENV/var/invenio.base-instance/static/")
    local("rm -rf inspire/base/static/gen/")
    local("rm -rf inspire/base/static/vendors/")
    local("inveniomanage bower -i bower-base.json > bower.json")
    local("bower install")
    local("inveniomanage collect")


@task
def compile_translations():
    """Compile the Invenio translations."""
    package = local("python setup.py --fullname", capture=True).strip()
    venv = "{0}/{1}".format(env.directory, package)
    if not exists(venv):
        return error("Meh? I need a virtualenv first.")
    with settings(sudo_user="invenio"):
        with cd("{0}/src/{1}".format(venv, package)):
            with prefix('source {0}/bin/activate'.format(venv)):
                prefix_folder = sudo('python -c "import invenio; print(invenio.__path__[0])"')
                prefix_folder = prefix_folder.split("\n")
                sudo("pybabel compile -fd {0}/base/translations".format(prefix_folder[-1]))
