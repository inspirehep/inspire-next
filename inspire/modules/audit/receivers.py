# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2015 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Signal receivers for audit."""
from inspire.modules.audit.models import Audit
from inspire.modules.audit.signals import audit_action_taken

def audit_action_received(sender, logging_info, **kwargs):
    audit = Audit()

    audit.object_id = logging_info["object_id"]
    audit.user_id = logging_info["user_id"]

    audit.score = logging_info["score"]
    audit.decision = logging_info["decision"]
    audit.user_action = logging_info["user_action"]

    audit.source = logging_info["source"]
    audit.action = logging_info["action"]

    audit.save()


audit_action_taken.connect(audit_action_received)