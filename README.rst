=================
INSPIRE overlay
=================

This is INSPIRE demo site source code overlay.  It installs on top of
Invenio digital library platform source code.


Installation
------------

``$ npm install``

``$ bower install``

``$ grunt prod`` *// copies the libraries and compiles LESS to CSS*

(optional) ``$ grunt dev`` *// a watcher auto compiles on save when developing on LESS file*


``bower`` and ``grunt`` not found:
----------------------------------

``$ npm install -g grunt-cli bower``

``node`` not found:
-------------------

Do ``$ which nodejs`` and create a softlink to it named node in the same directory where nodejs is located.

Note that some UNIX systems might have another utility called node already installed.
