# -*- coding: utf-8 -*-

"""Deployment of INSPIRE Labs."""

import json
import os

from fabric.api import *
from fabric.utils import error
from fabric.contrib.files import exists

env.directory = '/opt'  # remote directory
env.conf_directory = "/afs/cern.ch/project/inspire/repo/inspire-configuration.git"

env.roledefs = {
    'prod': ['inspirelabsvm01', 'inspirelabsvm02'],
    'prod1': ['inspirelabsvm01'],
    'prod2': ['inspirelabsvm02'],
    'dev01': ['inspirevm08.cern.ch'],
    'dev02': ['inspirevm11.cern.ch'],
    'proxy': ['inspirelb1.cern.ch'],
}


labs_backends = [
    "inspirelabs",
    "inspirelabs-ssl",
]

env.proxybackends = {
    'prod1': ['inspirelabsvm01', labs_backends],
    'prod2': ['inspirelabsvm02', labs_backends],
}


@task
def proxy():
    """Activate connection to proxy server."""
    env.hosts = env.roledefs['proxy']


@task
def prod():
    """Activate connection to labs production servers."""
    env.roles = ['prod']
    env.site_url = "http://labs.inspirehep.net"
    env.site_secure_url = "https://labs.inspirehep.net"
    env.conf_branch = "prod"
    env.tmp_shared = "/afs/cern.ch/project/inspire/LABS/var/tmp-shared"
    env.data = "/afs/cern.ch/project/inspire/LABS/var/data"
    env.log_bibsched = "/afs/cern.ch/project/inspire/LABS/var/log/bibsched"


@task
def prod1():
    """Activate connection to labs production server 1."""
    env.roles = ['prod1']
    env.site_url = "http://labs.inspirehep.net"
    env.site_secure_url = "https://labs.inspirehep.net"
    env.conf_branch = "prod"
    env.tmp_shared = "/afs/cern.ch/project/inspire/LABS/var/tmp-shared"
    env.data = "/afs/cern.ch/project/inspire/LABS/var/data"
    env.log_bibsched = "/afs/cern.ch/project/inspire/LABS/var/log/bibsched"


@task
def prod2():
    """Activate connection to labs production server 2."""
    env.roles = ['prod2']
    env.site_url = "http://labs.inspirehep.net"
    env.site_secure_url = "https://labs.inspirehep.net"
    env.conf_branch = "prod"
    env.tmp_shared = "/afs/cern.ch/project/inspire/LABS/var/tmp-shared"
    env.data = "/afs/cern.ch/project/inspire/LABS/var/data"
    env.log_bibsched = "/afs/cern.ch/project/inspire/LABS/var/log/bibsched"


@task
def vm08():
    """Activate connection to labs dev server 1."""
    env.roles = ['dev01']
    env.site_url = "http://inspirelabstest.cern.ch"
    env.site_secure_url = "https://inspirelabstest.cern.ch"
    env.conf_branch = "dev"
    env.tmp_shared = ""
    env.data = ""
    env.log_bibsched = ""


@task
def vm11():
    """Activate connection to labs dev server 2."""
    env.roles = ['dev02']
    env.site_url = "http://inspirevm11.cern.ch"
    env.site_secure_url = "https://inspirevm11.cern.ch"
    env.tmp_shared = ""
    env.data = ""
    env.log_bibsched = ""


@task
def pack():
    """Create a new source distribution as tarball for Inspire and Invenio."""
    with open(".bowerrc") as fp:
        bower = json.load(fp)

    choice = prompt("Clean and reinstall local assets? (y/N)", default="no")
    if choice.lower() in ["y", "ye", "yes"]:
        clean_assets()

    choice = prompt("Build assets to gen? (Y/n)", default="yes")
    if choice.lower() not in ["n", "no"]:
        local("inveniomanage assets build --directory {directory}/../gen".format(**bower))
    pack_invenio()
    return pack_inspire()


@task
def init_password():
    """Kickstart the password prompt."""
    sudo("echo 'hello world'")


@task
def pack_inspire():
    """Create a new source distribution as tarball without assets building (advanced use)."""
    return local("python setup.py sdist --formats=gztar", capture=False) \
        .succeeded


@task
def pack_invenio():
    """Create a new source distribution as tarball of Invenio."""
    virtualenv = os.environ["VIRTUAL_ENV"]
    with lcd(os.path.join(virtualenv, "src/invenio")):
        return local("python setup.py sdist --formats=gztar", capture=False).succeeded


@task
def create_virtualenv():
    """Create the virtualenv for the current Inspire version."""
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
    """Install all the things."""
    package = local("python setup.py --fullname", capture=True).strip()
    venv = "{0}/{1}".format(env.directory, package)

    if not exists(venv):
        return error("Meh? I need a virtualenv first.")

    success = 1
    invenio_package = ""

    # Upload the packages and put it into our virtualenv.
    virtualenv = os.environ["VIRTUAL_ENV"]
    put("dist/{0}.tar.gz".format(package), "/tmp/app.tgz")
    with lcd(os.path.join(virtualenv, "src/invenio")):
        invenio_package = local("python setup.py --fullname", capture=True).strip()
        put("dist/{0}.tar.gz".format(invenio_package), "/tmp/invenio.tgz")

    with settings(sudo_user="invenio"):
        sudo("mkdir -p {0}/src".format(venv))
        with cd("{0}/src".format(venv)):
            sudo("tar xzf /tmp/app.tgz")
            run("rm -rf /tmp/app.tgz")
            # Also Invenio
            sudo("tar xzf /tmp/invenio.tgz")
            run("rm -rf /tmp/invenio.tgz")

        # Invenio installation
        with cd("{0}/src/{1}".format(venv, invenio_package)):
            with prefix('source {0}/bin/activate'.format(venv)):
                sudo("pip install Babel")
                sudo("pip install numpy")
                sudo("pip install git+git://github.com/mrjoes/flask-admin.git#egg=Flask-Admin-1.0.9.dev0")
                sudo("python setup.py install")

        # Inspire installation
        with cd("{0}/src/{1}".format(venv, package)):
            with prefix('source {0}/bin/activate'.format(venv)):
                sudo("pip install git+https://github.com/inspirehep/python-rt#egg=rt")
                success = sudo("python setup.py install")
                if success:
                    # INSPIRE specific configuration
                    with cd(env.conf_directory):
                        config_location = "/tmp/inspire-configuration"
                        sudo("mkdir -p {0}".format(config_location))
                        sudo("GIT_WORK_TREE={0} git checkout -f {1}".format(config_location, env.conf_branch))
                        sudo("pip install {0} --upgrade".format(config_location))
                    # post install
                    sudo("inveniomanage collect")
                    with warn_only():
                        # Set Flask Host configuration
                        if "{0}" in env.site_url:
                            url = env.site_url.format(env.host)
                            secure_url = env.site_secure_url.format(env.host)
                        else:
                            url = env.site_url
                            secure_url = env.site_secure_url
                        sudo("inveniomanage config set CFG_SITE_URL {0}".format(url))
                        sudo("inveniomanage config set CFG_SITE_SECURE_URL {0}".format(secure_url))
                        # Create Apache configuration
                        sudo("inveniomanage apache create-config")
                        create_symlink("/opt/invenio", venv)
                        if env.tmp_shared:
                            create_symlink(os.path.join(venv, "var/tmp-shared", env.tmp_shared))
                        if env.data:
                            create_symlink(os.path.join(venv, "var/data", env.data))
                        if env.log_bibsched:
                            create_symlink(os.path.join(venv, "var/log/bibsched", env.log_bibsched))

        with cd("{0}/var".format(venv)):
            sudo("mkdir -p log/bibsched")
            create_symlink("/opt/invenio", venv)

    if success:
        sudo("supervisorctl restart celeryd")
        graceful_apache()
    return success


@task
def restart_celery():
    """Restart celery workers."""
    return sudo("supervisorctl restart celeryd")


@task
def restart_apache():
    """Restart celery workers."""
    return sudo("service httpd graceful")


@task
def graceful_apache():
    """Restart apache gracefully."""
    target = env.host
    execute(disable, target, False)
    execute(restart_apache)
    choice = prompt("{0} restarted. Enable host? (Y/n)".format(target), default="yes")
    if choice.lower() in ["y", "ye", "yes"]:
        execute(enable, target, False)


@task
def refresh_config():
    """Re-install the inspire-configuration ONLY."""
    package = local("python setup.py --fullname", capture=True).strip()
    venv = "{0}/{1}".format(env.directory, package)

    if not exists(venv):
        return error("Meh? I need a virtualenv first.")
    with settings(sudo_user="invenio"):
        with cd(venv):
            with prefix('source {0}/bin/activate'.format(venv)):
                # INSPIRE specific configuration
                with cd(env.conf_directory):
                    config_location = "/tmp/inspire-configuration"
                    sudo("mkdir -p {0}".format(config_location))
                    sudo("GIT_WORK_TREE={0} git checkout -f {1}".format(config_location, env.conf_branch))
                    sudo("pip install {0} --upgrade".format(config_location))
    restart_celery()
    restart_apache()


@task
def refresh_invenio():
    """Re-install the Invenio package ONLY (also builds it)."""
    virtualenv = os.environ["VIRTUAL_ENV"]
    package = ""
    with lcd(os.path.join(virtualenv, "src/invenio")):
        package = local("python setup.py --fullname", capture=True).strip()
        local("python setup.py sdist --formats=gztar", capture=False).succeeded
        put("dist/{0}.tar.gz".format(package), "/tmp/invenio.tgz")

    with settings(sudo_user="invenio"):
        # Invenio installation
        with cd("{0}/src/{1}".format(venv, package)):
            with prefix('source {0}/bin/activate'.format(venv)):
                sudo("python setup.py install")


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
                do_compilation()


def do_compilation():
    """Compile base Invenio translatation to avoid translation error."""
    prefix_folder = sudo('python -c "import invenio; print(invenio.__path__[0])"')
    prefix_folder = prefix_folder.split("\n")
    sudo("pybabel compile -fd {0}/base/translations".format(prefix_folder[-1]))


@roles(['proxy'])
@task
def disable(host, interactive=True):
    """Disable a server in the haproxy configuration. Use with proxy."""
    if isinstance(host, basestring):
        host = [host]

    backends = env.proxybackends
    if not backends:
        print("No backends defined")
        return

    server = None
    for alias, item in backends.items():
        # item = ('hostname', [list of backends])
        hostname, dummy_list_of_backends = item
        if hostname in host or alias in host:
            server = alias
            break
    if not server:
        print("No server defined")
        return

    servername, backends = backends[server]
    if interactive:
        choice = prompt("Disable the following server? %s (Y/n)" % (servername, ), default="yes")
        if choice.lower() not in ["y", "ye", "yes"]:
            return
    proxy_action(servername, backends, action="disable")


@roles(['proxy'])
@task
def enable(host, interactive=True):
    """Enable a server in the haproxy configuration. Use with proxy."""
    if isinstance(host, basestring):
        host = [host]

    backends = env.proxybackends
    if not backends:
        print("No backends defined")
        return

    server = None
    for alias, item in backends.items():
        # item = ('hostname', [list of backends])
        hostname, dummy_list_of_backends = item
        if hostname in host or alias in host:
            server = alias
            break
    if not server:
        print("No server defined")
        return

    servername, backends = backends[server]
    if interactive:
        choice = prompt("Enable the following server? %s (Y/n)" % (servername, ), default="yes")
        if choice.lower() not in ["y", "ye", "yes"]:
            return
    proxy_action(servername, backends, action="enable")


def proxy_action(server, backends, action="enable"):
    """Using sockets, communicate with haproxy."""
    for backend in backends:
        if 'ssl' in backend:
            # special ssl suffix
            current_server_suffix = '-ssl'
        else:
            current_server_suffix = ''
        current_server = server + current_server_suffix
        cmd = 'echo "%s server %s/%s" | nc -U /var/lib/haproxy/stats' \
               % (action, backend, current_server)
        sudo(cmd, shell=True)


def create_symlink(link, target):
    """Create a symlink if required."""
    existing_link = sudo("readlink {0}".format(link), capture=True)
    if existing_link and existing_link != target:
        sudo("rm {0}".format(link))
        sudo("ln -s {0} {1}".format(target, venv))
