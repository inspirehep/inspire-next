# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2014 CERN.
##
## INSPIRE is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""INSPIRE default access configuration."""

# Demo site roles
#           name          description          definition
DEF_DEMO_ROLES = (
    ('cataloger', 'Cataloger', 'deny all'),
    ('basketusers', 'Users who can use baskets', 'deny all'),
    ('claimpaperusers', 'Users who can perform changes to their own paper '
     'attributions without the need for an operator\'s approval',
     'allow any'),
)


# Demo site authorizations
#    role          action        arguments
DEF_DEMO_AUTHS = (
    ('cataloger', 'cfgbibknowledge', {}),
    ('cataloger', 'cfgbibsched', {}),
    ('cataloger', 'runinfomanager', {}),
    #('cataloger', 'runsearchuser', {}),  TODO: missing auth
    ('cataloger', 'runbibupload', {}),
    ('cataloger', 'runbibtasklet', {}),
    ('cataloger', 'runbibexport', {}),
    ('cataloger', 'runbibdocfile', {}),
    ('cataloger', 'runbatchuploader', {}),
    ('cataloger', 'runbibedit', {}),
    ('cataloger', 'runbibeditmulti', {}),
    ('cataloger', 'runbibmerge', {}),
    ('cataloger', 'viewholdingpen', {}),
    ('cataloger', 'viewauthorreview', {}),
)
