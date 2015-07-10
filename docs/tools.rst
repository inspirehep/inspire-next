INSPIRE workflow and tools
==========================

Available Fabric commands
-------------------------

You will find a `fabfile.py` in the root folder of this overlay. It is a compilation of tasks for `Fabric <http://www.fabfile.org/>`_

A useful one that you can use as a shortcut to completely recreate your assets is:

.. code-block:: bash

     (inspire)$ fab clean_assets

This will:

1. Remove all your static assets
2. Gather all the Bower dependencies and write them in the file `bower.json`
3. Execute `Bower install`
4. Execute `inveniomanage collect`

You should then find all your updated assets in `$ cdvirtualenv var/invenio.base-instance/static/`

Available Grunt commands
------------------------
The INSPIRE overlay contains some Grunt helpers that can help you with your JavaScript development. If you don't have such tools integrated in your IDE it is recommended to use them before submitting a PR.

You should already have `npm` installed if you followed the Invenio installation. So execute the following commands:

1. Install ``grunt-cli`` globally with ``npm install -g grunt-cli``.

2. Navigate to the root directory, then run ``npm install``. ``npm`` will look at package.json and automatically install the necessary local dependencies listed there.

| **Development**

``grunt jshint``

| This is a task to lint JavaScript according to `JSHint <http://www.jshint.com/>`_.

``grunt jsbeautifier``

| This is a task to prettifiy JavaScript according to `JSbeautifier <https://www.npmjs.org/package/grunt-jsbeautifier/>`_.
