# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

import os


def get_model_from_obj(obj):
    """Returns an instance of the model from the workflow."""
    from invenio_workflows.registry import workflows
    workflow = workflows.get(obj.workflow.name)

    if workflow is not None:
        return workflow.model(obj)
    else:
        return None


def get_record_from_obj(obj, eng):
    """Returns a Record instance of a BibWorkflowObject."""
    from invenio_records.api import Record

    model = eng.workflow_definition.model(obj)
    sip = model.get_latest_sip()
    return Record(sip.metadata)


def get_record_from_model(model):
    """Returns a Record instance of a model-like object."""
    from invenio_records.api import Record

    sip = model.get_latest_sip()
    return Record(sip.metadata)


def add_file_by_name(model, file_path, filename=None):
    """Save given file to storage and attach to object, return new path."""
    from inspire.modules.workflows.models import PayloadStorage
    from invenio_deposit.models import (
        Deposition,
        Agent,
        DepositionDraft,
        SubmissionInformationPackage,
        DepositionStorage,
        DepositionFile,
        FilenameAlreadyExists,
    )

    filename = filename or os.path.basename(file_path)
    try:
        with open(file_path) as fd:
            file_object = DepositionFile(backend=PayloadStorage(model.id))
            if file_object.save(fd, filename=filename):
                super(type(model), model).add_file(file_object)
                model.save()
    except FilenameAlreadyExists as e:
        file_object.delete()
        raise e
    if file_object.is_local():
        return file_object.get_syspath()
    else:
        return file_object.get_url()


def get_file_by_name(model, filename):
    """Get file by filename."""
    from werkzeug import secure_filename

    for f in model.files:
        if f.name == secure_filename(filename):
            return f
