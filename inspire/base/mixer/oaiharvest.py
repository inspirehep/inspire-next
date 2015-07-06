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

from six import with_metaclass as meta

from invenio.ext.mixer import MixerMeta
from invenio.modules.oaiharvester.models import OaiHARVEST
from invenio.modules.oairepository.models import OaiREPOSITORY


class OaiHARVESTMixer(meta(MixerMeta)):
    __model__ = OaiHARVEST


class OaiREPOSITORYMixer(meta(MixerMeta)):
    __model__ = OaiREPOSITORY


__all__ = ('OaiHARVESTMixer', 'OaiREPOSITORYMixer', )
