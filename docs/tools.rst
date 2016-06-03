..
    This file is part of INSPIRE.
    Copyright (C) 2015, 2016 CERN.

    INSPIRE is free software; you can redistribute it
    and/or modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation; either version 2 of the
    License, or (at your option) any later version.

    INSPIRE is distributed in the hope that it will be
    useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with INSPIRE; if not, write to the
    Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
    MA 02111-1307, USA.

    In applying this license, CERN does not
    waive the privileges and immunities granted to it by virtue of its status
    as an Intergovernmental Organization or submit itself to any jurisdiction.


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
