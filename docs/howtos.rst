..
    This file is part of INSPIRE.
    Copyright (C) 2016 CERN.

    INSPIRE is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    INSPIRE is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.

    In applying this licence, CERN does not waive the privileges and immunities
    granted to it by virtue of its status as an Intergovernmental Organization
    or submit itself to any jurisdiction.


HOWTOs
======


1. Caching
----------


For caching we use Flask-Caching_. For example, to set a value in the cache:

.. code-block:: python

    from inspirehep.modules.cache import current_cache
    current_cache.set('test', [1, 2, 3], timeout=60)

And to retrieve the value from the cache:

.. code-block:: python

    from inspirehep.modules.cache import current_cache
    current_cache.get('test')


.. _Flask-Caching: https://pythonhosted.org/Flask-Caching/


2. Docker
---------


Currently INSPIRE supports two methods of installation :doc:installation_


2.1 Docker on Linux
^^^^^^^^^^^^^^^^^^^


TODO


2.2 Docker on Mac
^^^^^^^^^^^^^^^^^


We can't recommend using `Docker for Mac`_, because it results in
hard-to-understand bugs and not-very-good performance.

Instead, we recommend installing VirtualBox_ and Vagrant_ by either following
those links or running:

.. code-block:: shell-session

    $ brew cask install virtualbox
    $ brew cask install vagrant

Then, in a folder of your choosing, put the following ``VagrantFile``:

.. code-block:: ruby

    # -*- mode: ruby -*-
    # vi: set ft=ruby :

    Vagrant.configure(2) do |config|
      config.vm.box = "williamyeh/ubuntu-trusty64-docker"

      config.vm.network "forwarded_port", guest: 5000, host: 5000
      config.vm.network "forwarded_port", guest: 5555, host: 5555
      config.vm.network "forwarded_port", guest: 9200, host: 9200

      config.vm.provider "virtualbox" do |v|
        v.memory = 4096
        v.cpus = 2
      end
    end

Now you can run

.. code-block:: shell-session

    $ vagrant up
    $ vagrant ssh

to log in an Ubuntu machine with ``docker`` and ``docker-compose`` already
installed, and resume the installation from `2.1 Docker on Linux`_.


.. _`Docker for Mac`: https://docs.docker.com/engine/installation/mac/#/docker-for-mac
.. _Vagrant: https://www.vagrantup.com/downloads.html
.. _VirtualBox: https://www.virtualbox.org/wiki/Downloads


3. Profiling
------------


3. 1 Profiling a Celery Task
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To profile a Celery task we need to make sure that the task is executed by the
same Python process in which we are collecting the profiling information. That
is, the configuration must contain

.. code-block:: python

    CELERY_ALWAYS_EAGER = True
    CELERY_RESULT_BACKEND = 'cache'
    CELERY_CACHE_BACKEND = 'memory'

Then, in a Flask shell, we do

.. code-block:: python

    >>> import cProfile
    >>> import pstats
    >>> from path.to.our.task import task
    >>> pr = cProfile.Profile()
    >>> pr.runcall(task, *args, **kwargs)

where ``*args`` and ``*kwargs`` are the arguments and keyword arguments that
we want to pass to ``task``. Then

.. code-block:: python

    >>> ps = pstats.Stats(pr)
    >>> ps.dump_stats('task.prof')

will create a binary file containing the desired profiling information. To read
it we can use snakeviz_, which will create a graph such as

.. figure:: images/snakeviz.png
  :align: center
  :alt: An example of a snakeviz graph.
  :scale: 35%

To understand it, we refer to the `documentation of snakeviz`_.

.. _snakeviz: https://github.com/jiffyclub/snakeviz
.. _`documentation of snakeviz`: https://jiffyclub.github.io/snakeviz/#interpreting-results


3.2 Profiling a Request
^^^^^^^^^^^^^^^^^^^^^^^

To profile a request we need to add the following variable to our configuration:

.. code-block:: python

    PROFILE = True

Then we need to attach the `WSGI application profiler`_ to our WSGI application.
To do this, we need to add a few lines at the bottom of ``inspirehep/wsgi.py``:

.. code-block:: python

    import os; os.mkdir('prof')
    from werkzeug.contrib.profiler import ProfilerMiddleware
    application = ProfilerMiddleware(application, profile_dir='prof')

Now, after we restart the application, a profile report will be created in the
``prof`` folder for each request that we make. These binary files can be
visualized as above with snakeviz_.

.. _`WSGI application profiler`: http://werkzeug.pocoo.org/docs/0.11/contrib/profiler/
