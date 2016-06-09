
.. image:: https://coveralls.io/repos/inspirehep/inspire-next/badge.svg?branch=master&service=github
  :target: https://coveralls.io/github/inspirehep/inspire-next?branch=master

.. image:: https://travis-ci.org/inspirehep/inspire-next.svg?branch=master
    :target: https://travis-ci.org/inspirehep/inspire-next

===============
INSPIRE overlay
===============

This is the INSPIRE source code overlay for Invenio v.3.0. It installs on top of
Invenio Digital Library platform source code. The overlay is currently used for `<http://labs.inspirehep.net>`_


Latest news
===========

*2015-11-24: ElasticSearch 2.0 now required!*

Update your ElasticSearch installation and in order fetch updated packages you
need to run:

``pip install -r requirements.txt``

PS: This will override some invenio modules, so be sure to keep an eye on
what is re-installed in case you have installed them in development mode.


Installation
============

See the `install guide`_ here.

.. _install guide: ./INSTALL.rst


==============
Happy hacking!
==============

| INSPIRE Development Team
|   Email: admin@inspirehep.net
|   Twitter: @inspirehep
|   URL: http://inspirehep.net
