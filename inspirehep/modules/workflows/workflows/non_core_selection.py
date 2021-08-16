# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# inspirehep is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.\
from __future__ import absolute_import, division, print_function
from invenio_workflows import ObjectStatus


def set_object_status_to_completed(obj, eng):
    obj.status = ObjectStatus.COMPLETED


class NonCoreSelection(object):
    """Workflow for bookkeeping not core workflows marked as core"""

    name = "non_core_selection"
    data_type = "hep"

    workflow = [set_object_status_to_completed]
