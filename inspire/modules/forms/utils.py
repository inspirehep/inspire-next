#
## This file is part of INSPIRE.
## Copyright (C) 2015 CERN.
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
#

from wtforms import Field, FieldList, Form, FormField


class FormVisitor(object):
    """
    Generic form visitor to iterate over all fields in a form. See DataExporter
    for example how to export all data.
    """
    def visit(self, form_or_field):
        if isinstance(form_or_field, FormField):
            self.visit_formfield(form_or_field)
        elif isinstance(form_or_field, FieldList):
            self.visit_fieldlist(form_or_field)
        elif isinstance(form_or_field, Form):
            self.visit_form(form_or_field)
        elif isinstance(form_or_field, Field):
            self.visit_field(form_or_field)

    def visit_form(self, form):
        for field in form:
            self.visit(field)

    def visit_field(self, field):
        pass

    def visit_fieldlist(self, fieldlist):
        for field in fieldlist.get_entries():
            self.visit(field)

    def visit_formfield(self, formfield):
        self.visit(formfield.form)


class DataExporter(FormVisitor):
    """
    Visitor to export form data into dictionary supporting filtering and key
    renaming.

    Usage::
        form = ...
        visitor = DataExporter(filter_func=lambda f: not f.flags.disabled)
        visitor.visit(form)

    Given e.g. the following form::

        class MyForm(WebDepositForm):
            title = TextField(export_key='my_title')
            notes = TextAreaField()
            authors = FieldList(FormField(AuthorForm))

    the visitor will export a dictionary similar to::

        {'my_title': ..., 'notes': ..., authors: [{...}, ...], }
    """
    def __init__(self, filter_func=None):
        self.data = {}
        self.data_stack = [self.data]

        if filter_func is not None:
            self.filter_func = filter_func
        else:
            self.filter_func = lambda f: True

    def _export_name(self, field):
        """ Get dictionary key - defaults to field name """
        return field.export_key if getattr(field, 'export_key', None) \
            else field.short_name

    #
    # Stack helper methods
    #
    def _top_stack_element(self):
        return self.data_stack[-1]

    def _pop_stack(self):
        self.data_stack.pop()

    def _push_stack(self, field, prototype):
        data = self._top_stack_element()

        if isinstance(data, list):
            data.append(prototype)
            self.data_stack.append(data[-1])
        else:
            data[self._export_name(field)] = prototype
            self.data_stack.append(data[self._export_name(field)])

    #
    # Visit methods
    #
    def visit_field(self, field):
        if (self.filter_func)(field):
            data = self._top_stack_element()
            if isinstance(data, list):
                data.append(field.data)
            else:
                data[self._export_name(field)] = field.data

    def visit_formfield(self, formfield):
        if (self.filter_func)(formfield):
            self._push_stack(formfield, {})
            super(DataExporter, self).visit_formfield(formfield)
            self._pop_stack()

    def visit_fieldlist(self, fieldlist):
        if (self.filter_func)(fieldlist):
            self._push_stack(fieldlist, [])
            super(DataExporter, self).visit_fieldlist(fieldlist)
            self._pop_stack()
