# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
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
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, division, print_function

from wtforms import Field, FieldList, Form, FormField


CFG_GROUPS_META = {
    'classes': None,
    'indication': None,
    'description': None,
    'icon': None,
}
"""Default group metadata."""


CFG_FIELD_FLAGS = [
    'hidden',
    'disabled',
    'touched',
]
"""List of WTForm field flags to be saved in draft."""


class INSPIREForm(Form):

    """Generic WebDeposit Form class."""

    def __init__(self, *args, **kwargs):
        """Init."""
        super(INSPIREForm, self).__init__(*args, **kwargs)
        if not hasattr(self, 'template'):
            self.template = 'deposit/run.html'

        self.type = self.__class__.__name__

    # def reset_field_data(self, exclude=[]):
    #     """
    #     Reset the fields.data value to that of field.object_data.
    #     Useful after initializing a form with both formdata and draftdata where
    #     the formdata is missing field values (usually because we are saving a
    #     single field).
    #     @param exclude: List of field names to exclude.
    #     """
    #     for field in self._fields.values():
    #         field.reset_field_data(exclude=exclude)

    def get_groups(self):
        """Get a list of the (group metadata, list of fields)-tuples.
        The last element of the list has no group metadata (i.e. None),
        and contains the list of fields not assigned to any group.
        """
        fields_included = set()
        field_groups = []

        if hasattr(self, 'groups'):
            for group in self.groups:
                group_obj = {
                    'name': group[0],
                    'meta': CFG_GROUPS_META.copy(),
                }

                fields = []
                for field_name in group[1]:
                    if field_name in ['-', ]:
                        fields.append(field_name)
                    else:
                        try:
                            fields.append(self[field_name])
                            fields_included.add(field_name)
                        except KeyError:
                            pass

                if len(group) == 3:
                    group_obj['meta'].update(group[2])

                field_groups.append((group_obj, fields))

        # Append missing fields not defined in groups
        rest_fields = []
        for field in self:
            if field.name not in fields_included:
                rest_fields.append(field)
        if rest_fields:
            field_groups.append((None, rest_fields))

        return field_groups

    def get_template(self):
        """Get template to render this form.
        Define a data member `template` to customize which template to use.
        By default, it will render the template `deposit/run.html`
        """
        return [self.template]

    def post_process(self, form=None, formfields=[], submit=False):
        """Run form post-processing.

        Run form post-processing by calling `post_process` on each field,
        passing any extra `Form.post_process_<fieldname>` processors to the
        field.

        If `formfields` are specified, only the given fields' processors will
        be run (which may touch all fields of the form).
        The post processing allows the form to alter other fields in the form,
        via e.g. contacting external services (e.g a DOI field could retrieve
        title, authors from CrossRef/DataCite).
        """
        if form is None:
            form = self

        for name, field, in self._fields.items():
            inline = getattr(
                self, 'post_process_%s' % name, None)
            if inline is not None:
                extra = [inline]
            else:
                extra = []
            field.post_process(form, formfields=formfields,
                               extra_processors=extra, submit=submit)


    @property
    def json_data(self):
        """Return form data in a format suitable for the standard JSON encoder.
        Return form data in a format suitable for the standard JSON encoder, by
        calling Field.json_data() on each field if it exists, otherwise is uses
        the value of Field.data.
        """
        return dict(
            (name, f.json_data if getattr(f, 'json_data', None) else f.data)
            for name, f in self._fields.items()
        )

    @property
    def messages(self):
        """Return a dictionary of form messages."""
        _messages = {}

        for f in self._fields.values():
            _messages.update(f.messages)

        return dict([
            (
                fname,
                msgs if msgs.get('state', '') or msgs.get('messages', '')
                else {}
            ) for fname, msgs in _messages.items()
        ])

        return _messages


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

        class MyForm(INSPIREForm):
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
