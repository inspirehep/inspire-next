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
