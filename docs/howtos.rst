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
==========

1. Caching
----------


For caching we use Flask-cache_. For example, to set a value in the cache:

.. code-block:: python

    from inspirehep.modules.cache import current_cache
    current_cache.set('test', [1, 2, 3], timeout=60)

And to retrieve the value from the cache:

.. code-block:: python

    from inspirehep.modules.cache import current_cache
    current_cache.get('test')


.. _Flask-cache: https://pythonhosted.org/Flask-Cache/


2. Profiling
------------


2.1 Profiling a Celery Task
---------------------------

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
