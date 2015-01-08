# -*- coding: utf-8 -*-

"""Deployment of INSPIRE Labs."""

import json
import os

from fabric.api import *
from fabric.utils import error
from fabric.contrib.files import exists

env.directory = '/opt'  # remote directory
env.conf_directory = "/afs/cern.ch/project/inspire/repo/inspire-configuration.git"
env.backend_node = False

env.roledefs = {
    'prod': ['inspirelabsvm01', 'inspirelabsvm02'],
    'workers': ['inspirevm24', 'inspirevm25'],
    'prod1': ['inspirelabsvm01'],
    'prod2': ['inspirelabsvm02'],
    'worker1': ['inspirevm24'],
    'worker2': ['inspirevm25'],
    'dev01': ['inspirevm08.cern.ch'],
    'dev02': ['inspirevm11.cern.ch'],
    'proxy': ['inspirelb1.cern.ch'],
    'builder': ["inspirevm24"],
    'targets': ["inspirevm25", "inspirelabsvm01", "inspirelabsvm02"]  # hosts the builder syncs to
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
def workers():
    """Activate connection to labs production servers."""
    env.roles = ['workers']
    env.site_url = "http://labs.inspirehep.net"
    env.site_secure_url = "https://labs.inspirehep.net"
    env.conf_branch = "prod"
    env.tmp_shared = "/afs/cern.ch/project/inspire/LABS/var/tmp-shared"
    env.data = "/afs/cern.ch/project/inspire/LABS/var/data"
    env.log_bibsched = "/afs/cern.ch/project/inspire/LABS/var/log/bibsched"
    env.backend_node = True


@task
def worker1():
    """Activate connection to labs production servers."""
    env.roles = ['worker1']
    env.site_url = "http://labs.inspirehep.net"
    env.site_secure_url = "https://labs.inspirehep.net"
    env.conf_branch = "prod"
    env.tmp_shared = "/afs/cern.ch/project/inspire/LABS/var/tmp-shared"
    env.data = "/afs/cern.ch/project/inspire/LABS/var/data"
    env.log_bibsched = "/afs/cern.ch/project/inspire/LABS/var/log/bibsched"
    env.backend_node = True


@task
def worker2():
    """Activate connection to labs production servers."""
    env.roles = ['worker2']
    env.site_url = "http://labs.inspirehep.net"
    env.site_secure_url = "https://labs.inspirehep.net"
    env.conf_branch = "prod"
    env.tmp_shared = "/afs/cern.ch/project/inspire/LABS/var/tmp-shared"
    env.data = "/afs/cern.ch/project/inspire/LABS/var/data"
    env.log_bibsched = "/afs/cern.ch/project/inspire/LABS/var/log/bibsched"
    env.backend_node = True


@task
def builder():
    """Activate connection to labs production servers."""
    env.roles = ['builder']
    env.site_url = "http://labs.inspirehep.net"
    env.site_secure_url = "https://labs.inspirehep.net"
    env.conf_branch = "prod"
    env.tmp_shared = "/afs/cern.ch/project/inspire/LABS/var/tmp-shared"
    env.data = "/afs/cern.ch/project/inspire/LABS/var/data"
    env.log_bibsched = "/afs/cern.ch/project/inspire/LABS/var/log/bibsched"
    env.backend_node = True


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
    env.backend_node = True


@task
def vm11():
    """Activate connection to labs dev server 2."""
    env.roles = ['dev02']
    env.site_url = "http://inspirevm11.cern.ch"
    env.site_secure_url = "https://inspirevm11.cern.ch"
    env.tmp_shared = ""
    env.data = ""
    env.log_bibsched = ""
    env.backend_node = True


@task
def dry():
    """Activate dry run."""
    env.dry = True


@task
def pack():
    """Create a new source distribution as tarball for Inspire and Invenio."""
    with open(".bowerrc") as fp:
        bower = json.load(fp)

    with warn_only():
        if "True" in local("inveniomanage config get ASSETS_DEBUG", capture=True):
            print("You need to set ASSETS_DEBUG to False!")
            return 1

        if "flask.ext.collect.storage.link" in local("inveniomanage config get COLLECT_STORAGE", capture=True):
            print("COLLECT_STORAGE cannot be set to 'flask.ext.collect.storage.link'")
            return 1

    choice = prompt("Clean and reinstall local assets? (y/N)", default="no")
    if choice.lower() in ["y", "ye", "yes"]:
        clean_assets()

    choice = prompt("Build assets to gen? (Y/n)", default="yes")
    if choice.lower() not in ["n", "no"]:
        choice = prompt("Clean and reinstall local assets? (Y/n)", default="yes")
        if choice.lower() not in ["n", "no"]:
            clean_assets()
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

    if not env.backend_node:
        execute(disable, env.host, False)
    else:
        stop_celery()
        stop_bibsched()

    success = 1
    invenio_package = ""

    # Upload the packages and put it into our virtualenv.
    virtualenv = os.environ["VIRTUAL_ENV"]
    run("rm -rf /tmp/app.tgz")
    put("dist/{0}.tar.gz".format(package), "/tmp/app.tgz")
    with lcd(os.path.join(virtualenv, "src/invenio")):
        invenio_package = local("python setup.py --fullname", capture=True).strip()
        run("rm -rf /tmp/invenio.tgz")
        put("dist/{0}.tar.gz".format(invenio_package), "/tmp/invenio.tgz")

    remove_build()
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
                sudo("pip install . --upgrade")

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
                            create_symlink(os.path.join(venv, "var/tmp-shared"), env.tmp_shared)
                        if env.data:
                            create_symlink(os.path.join(venv, "var/data"), env.data)
                        if env.log_bibsched:
                            create_symlink(os.path.join(venv, "var/log/bibsched"), env.log_bibsched)

        with cd("{0}/var".format(venv)):
            sudo("mkdir -p log/bibsched")

    if success:
        restart_apache()
        if not env.backend_node:
            execute(enable, env.host, True)
        else:
            choice = prompt("Enable backend (Celery, BibSched)? (Y/n)", default="yes")
            if choice.lower() in ["y", "ye", "yes"]:
                start_celery()
                start_bibsched()
    return success


@roles(['builder'])
@task
def sync(host="targets"):
    """Sync Invenio to given host (or all)."""
    package = local("python setup.py --fullname", capture=True).strip()
    venv = "{0}/{1}".format(env.directory, package)

    if not exists(venv):
        return error("Meh? I need a virtualenv first.")

    for current_host in env.roledefs[host]:
        execute(disable, current_host, False)
        sudo(
            'rsync -az --force --delete --progress -h '
            '--exclude "var/tmp-shared" --exclude "src" '
            '--exclude "var/log" --exclude "var/data" '
            '--exclude "var/tmp" --exclude "var/run" '
            '--exclude "var/cache" --exclude "var/batchupload" '
            '--exclude "etc" --exclude "includes" '
            '--exclude "var/invenio.base-instance/apache" '
            '--exclude "var/invenio.base-instance/run" '
            '-e "ssh -p22" {venv}/ {server}:/opt/invenio'.format(venv=venv, server=current_host)
        )
        with settings(host_string=current_host):
            restart_apache()
        execute(enable, current_host, False)


@task
def remove_build():
    """Remove the leftover build directory."""
    package = local("python setup.py --fullname", capture=True).strip()
    venv = "{0}/{1}".format(env.directory, package)
    with settings(sudo_user="invenio"):
        with prefix('source {0}/bin/activate'.format(venv)):
            build_dir = os.path.join(venv, "build")
            src_dir = os.path.join(venv, "src")
            sudo("rm -rf {0}".format(src_dir))
            sudo("rm -rf {0}".format(build_dir))


@task
def restart_celery():
    """Restart celery workers."""
    return sudo("supervisorctl restart celeryd")


@task
def stop_celery():
    """Restart celery workers."""
    return sudo("supervisorctl stop celeryd")


@task
def start_celery():
    """Restart celery workers."""
    return sudo("supervisorctl start celeryd")


@task
def stop_bibsched():
    """Restart celery workers."""
    package = local("python setup.py --fullname", capture=True).strip()
    venv = "{0}/{1}".format(env.directory, package)
    with settings(sudo_user="invenio"):
        with prefix('source {0}/bin/activate'.format(venv)):
            return sudo("bibsched stop")


@roles(['workers'])
@task
def stop():
    """Restart celery workers."""
    stop_bibsched()
    stop_celery()


@roles(['workers'])
@task
def start():
    """Restart celery workers."""
    start_bibsched()
    start_celery()


@task
def start_bibsched():
    """Restart celery workers."""
    package = local("python setup.py --fullname", capture=True).strip()
    venv = "{0}/{1}".format(env.directory, package)
    with settings(sudo_user="invenio"):
        with prefix('source {0}/bin/activate'.format(venv)):
            return sudo("bibsched start")


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
    execute(enable, target, True)


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
    graceful_apache()


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
        with cd("{0}/src/{1}".format(venv, invenio_package)):
            with prefix('source {0}/bin/activate'.format(venv)):
                sudo("pip install Babel")
                sudo("pip install numpy")
                sudo("pip install . --upgrade")


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
    existing_link = sudo("readlink {0}".format(link))
    if existing_link:
        if existing_link != target:
            sudo("rm {0}".format(link))
            sudo("ln -s {0} {1}".format(target, link))
        else:
            return
    else:
        sudo("ln -s {0} {1}".format(target, link))
