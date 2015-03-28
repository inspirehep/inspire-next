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

from wtforms import Field

__all__ = ('InspireField', )


class InspireField(Field):

    """Base field that all fields in INSPIRE should inherit from."""

    def __init__(self, *args, **kwargs):
        self.placeholder = kwargs.pop('placeholder', None)
        self.icon = kwargs.pop('icon', None)
        self.export_key = kwargs.pop('export_key', None)
        self.widget_classes = kwargs.pop('widget_classes', None)

        super(InspireField, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if 'placeholder' not in kwargs and self.placeholder:
            kwargs['placeholder'] = self.placeholder
        if 'class_' in kwargs and self.widget_classes:
            kwargs['class_'] = kwargs['class_'] + self.widget_classes
        elif self.widget_classes:
            kwargs['class_'] = self.widget_classes
        return super(InspireField, self).__call__(*args, **kwargs)
