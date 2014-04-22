=================
INSPIRE overlay
=================

This is INSPIRE demo site source code overlay.  It installs on top of
Invenio digital library platform source code.

--------------------------
INSPIRE workflow and tools
--------------------------

INSPIRE uses `Grunt <http://gruntjs.com/>`_ and `Bower <http://bower.io/>`_ with convenient methods for compiling code, run tasks, install libraries and more. To use them, install the required dependencies as directed and then run some Grunt commands.

Install Grunt
-------------

From the command line:

1. Install ``grunt-cli`` globally with ``npm install -g grunt-cli``.

2. Navigate to the root directory, then run ``npm install``. ``npm`` will look at package.json and automatically install the necessary local dependencies listed there.


| When completed, you'll be able to run the various Grunt commands provided from the command line.

| **Unfamiliar with npm? Don't have node installed?** That's a-okay. npm stands for `node packaged modules <https://www.npmjs.org/>`_ and is a way to manage development dependencies through node.js. `Download and install node.js <http://nodejs.org/download/>`_ before proceeding.

Install Bower
-------------

From the command line:

1. Install ``bower`` globally with ``npm install -g bower``.

2. Navigate to the root directory, then run ``bower install``. ``bower`` will look at bower.json and automatically install the necessary local dependencies listed there.


| When completed, you'll have all the dependencies under ``bower_components/``.

Available Grunt commands
------------------------

**Build** - ``grunt``

| Run ``grunt`` to compile LESS to CSS into ``inspire.css``. Uses `Less <http://lesscss.org/>`_.

| **Development** - ``grunt watch``

| This is a convenience method for watching just Less files and automatically building them whenever you save.

Troubleshooting dependencies
----------------------------

Should you encounter problems with installing dependencies or running Grunt commands, uninstall all previous dependency versions (global and local). Then, rerun ``npm install``.