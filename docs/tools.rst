INSPIRE tools & scripts
=======================

Available Bash scripts
----------------------

You will find a `scripts` folder in the root folder of this overlay. It is a compilation of useful scripts to setup demo records, rebuild assets etc.

A useful one that you can use as a shortcut to completely recreate your assets is:

.. code-block:: bash

     (inspire)$ ./scripts/clean_assets

This will:

1. Remove all your static assets
2. Gather all the npm dependencies and write them in the file `package.json` in the instance static folder
3. Execute `npm install`
4. Execute `inspirehep collect` and `inspirehep assets build`

You should then find all your updated assets in `$ cdvirtualenv var/inspirehep-instance/static/`
