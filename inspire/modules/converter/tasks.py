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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

import traceback

from functools import wraps


def convert_record(stylesheet="oaidc2marcxml.xsl"):
    """Convert the object data to marcxml using the given stylesheet.

    :param stylesheet: which stylesheet to use
    :return: function to convert record
    :raise WorkflowError:
    """
    @wraps(convert_record)
    def _convert_record(obj, eng):
        from invenio_workflows.errors import WorkflowError
        from .xslt import convert

        eng.log.info("Starting conversion using %s stylesheet" %
                     (stylesheet,))

        if not obj.data:
            obj.log.error("Not valid conversion data!")
            raise WorkflowError("Error: conversion data missing",
                                id_workflow=eng.uuid,
                                id_object=obj.id)
        try:
            obj.data = convert(obj.data, stylesheet)
        except Exception as e:
            msg = "Could not convert record: %s\n%s" % \
                  (str(e), traceback.format_exc())
            raise WorkflowError("Error: %s" % (msg,),
                                id_workflow=eng.uuid,
                                id_object=obj.id)

    _convert_record.description = 'Convert record'
    return _convert_record


def convert_encoding(from_encoding="ISO-8859-1", to_encoding="UTF-8"):
    """Convert obj.data string from one encoding to another."""
    @wraps(convert_encoding)
    def _convert_encoding(obj, dummy):
        try:
            obj.data = obj.data.encode(from_encoding).decode(to_encoding)
        except (UnicodeEncodeError, UnicodeDecodeError) as err:
            obj.log.error(err)
    return _convert_encoding
