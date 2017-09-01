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

"""Implement custom field widgets."""

from __future__ import absolute_import, division, print_function

from inspirehep.utils.template import render_macro_from_template

from wtforms.widgets import HiddenInput, HTMLString, Input, RadioInput, \
    TextInput, html_params


class ButtonWidget(object):

    """Implement Bootstrap HTML5 button."""

    def __init__(self, label="", tooltip=None, icon=None, **kwargs):
        """Initialize button widget.

        .. note:: the icons assume use of Twitter Bootstrap,
        Font Awesome or some other icon library, that allows
        inserting icons with a <i>-tag.

        :param tooltip: str, Tooltip text for the button.
        :param icon: str, Name of an icon, e.g. icon-barcode.
        """
        self.icon = icon
        self.label = label
        self.default_params = kwargs
        self.default_params.setdefault('type', 'button')
        if tooltip:
            self.default_params.setdefault('data-toggle', 'tooltip')
            self.default_params.setdefault('title', tooltip)
        super(ButtonWidget, self).__init__()

    def __call__(self, field, **kwargs):
        """Render button widget."""
        params = self.default_params.copy()
        params.update(kwargs)
        params.setdefault('id', field.id)
        params['class_'] = params.get('class_', "") + " form-button"

        icon = ""
        if self.icon:
            icon = '<i class="%s"></i> ' % self.icon

        state = ""
        if field._value():
            state = ('<span class="text-success"> '
                     '<i class="glyphicon glyphicon-ok"></i></span>')

        return HTMLString(u'<button %s>%s%s</button><span %s>%s</span>' % (
            html_params(name=field.name, **params),
            icon,
            self.label,
            html_params(id=field.name + '-loader', class_='loader'),
            state,
        ))


class TagInput(Input):

    """Implement tag input widget."""

    input_type = 'hidden'

    def __call__(self, field, **kwargs):
        """Render tag input widget."""
        if "__input__" in field.name:
            self.input_type = 'text'
            html = super(TagInput, self).__call__(field, **kwargs)
            self.input_type = 'hidden'
        else:
            return super(TagInput, self).__call__(field, **kwargs)

        return html


class WrappedInput(Input):

    """Widget to wrap text input in further markup."""

    wrapper = '<div>%(field)s</div>'
    wrapped_widget = TextInput()

    def __init__(self, widget=None, wrapper=None, **kwargs):
        """Initialize wrapped input with widget and wrapper."""
        self.wrapped_widget = widget or self.wrapped_widget
        self.wrapper_args = kwargs
        if wrapper is not None:
            self.wrapper = wrapper

    def __call__(self, field, **kwargs):
        """Render wrapped input."""
        return HTMLString(self.wrapper % dict(
            field=self.wrapped_widget(field, **kwargs),
            **self.wrapper_args
        ))


class ColumnInput(WrappedInput):

    """Specialized column wrapped input."""

    @property
    def wrapper(self):
        """Wrapper template with description support."""
        if 'description' in self.wrapper_args:
            return ('<div class="%(class_)s">%(field)s'
                    '<p class="text-muted field-desc">'
                    '<small>%(description)s</small></p></div>')
        return '<div class="%(class_)s">%(field)s</div>'


#
# Item widgets
#
class ItemWidget(object):

    """Render each subfield without additional markup around the subfield."""

    def __call__(self, subfield, **kwargs):
        """Render given ``subfield``."""
        return subfield()


class ListItemWidget(ItemWidget):

    """Render each subfield in a ExtendedListWidget as a list element.

    If `with_label` is set, the fields label will be rendered. If
    `prefix_label` is set, the label will be prefixed, otherwise it will be
    suffixed.
    """

    def __init__(self, html_tag='li', with_label=True, prefix_label=True,
                 class_=None):
        """Initialize list item with html tag.

        :param html_tag: name of html tag can be 'li', 'div', or 'span'.
        """
        assert html_tag in ('li', 'div', 'span', None)
        self.html_tag = html_tag
        self.prefix_label = prefix_label
        self.with_label = with_label
        self.class_ = class_

    def render_subfield(self, subfield, **kwargs):
        """Render subfield."""
        if self.with_label:
            if self.prefix_label:
                return '%s: %s' % (subfield.label, subfield())
            else:
                return '%s %s' % (subfield(), subfield.label)
        else:
            return subfield()

    def open_tag(self, subfield, **kwargs):
        """Return open tag."""
        if self.html_tag:
            return '<%s %s>' % (
                self.html_tag,
                html_params(class_=self.class_ or kwargs.get('class_', ''))
            )
        return ''

    def close_tag(self, subfield, **kwargs):
        """Return close tag."""
        if self.html_tag:
            return '</%s>' % self.html_tag
        return ''

    def __call__(self, subfield, **kwargs):
        """Render list item widget."""
        html = [self.open_tag(subfield, **kwargs)]
        html.append(self.render_subfield(subfield, **kwargs))
        html.append(self.close_tag(subfield, **kwargs))
        return HTMLString(''.join(html))


class DynamicItemWidget(ListItemWidget):

    """Render each subfield in a ExtendedListWidget enclosed in a div.

    It adds also tag with buttons for sorting and removing the item.
    I.e. something like:

    .. code-block:: jinja

        <div><span>"buttons</span>:field</div>

    """

    def __init__(self, **kwargs):
        """Initialize dynamic item widget."""
        self.icon_reorder = kwargs.pop('icon_reorder', 'fa fa-sort fa-fw')
        self.icon_remove = kwargs.pop('icon_remove', 'fa fa-times fa-fw')
        defaults = dict(
            html_tag='div',
            with_label=True,
        )
        defaults.update(kwargs)
        super(DynamicItemWidget, self).__init__(**defaults)

    def _sort_button(self):
        return ("""<a class="sort-element text-muted sortlink iconlink" """
                """rel="tooltip" title="Drag to reorder"><i class="%s">"""
                """</i></a>""" % self.icon_reorder)

    def _remove_button(self):
        return ("""<a class="remove-element text-muted iconlink" """
                """rel="tooltip" title="Click to remove"><i class="%s">"""
                """</i></a>""" % self.icon_remove)

    def render_subfield(self, subfield, **kwargs):
        """Render subfield."""
        html = []

        html.append("<div %s>" % html_params(class_='row'))
        # Field
        html.append(subfield())
        # Buttons
        html.append("<div %s>%s</div>" % (
            html_params(class_='col-xs-2'),
            self._sort_button() + self._remove_button()
        ))
        html.append("</div>")
        return ''.join(html)

    def __call__(self, subfield, **kwargs):
        """Render dynamic item widget."""
        kwargs.setdefault('id', 'element-' + subfield.id)
        # Are we rendering an empty form element?
        empty_index = kwargs.pop('empty_index', '__index__')
        if subfield.name.endswith(empty_index):
            kwargs['class_'] = kwargs.get('class_', '') + ' empty-element'
        elif subfield.name.endswith('__input__'):
            kwargs['class_'] = kwargs.get('class_', '') + ' input-element'
        else:
            # for deposit form
            kwargs['class_'] = kwargs.get('class_', '') + ' field-list-element'
        return super(DynamicItemWidget, self).__call__(subfield, **kwargs)


#
# List widgets
#
class ExtendedListWidget(object):

    """Render a list of fields as a `ul`, `ol` or `div` list.

    This is used for fields which encapsulate a list of other fields as
    subfields. The widget will try to iterate the field to get access to the
    subfields and call them to render them.

    The `item_widget` decide how subfields are rendered, and usually just
    provide a thin wrapper around the subfields render method. E.g.
    ExtendedListWidget renders the ul-tag, while the ListItemWidget renders
    each li-tag. The content of the li-tag is rendered by the subfield's
    widget.
    """

    item_widget = ListItemWidget()

    def __init__(self, html_tag='ul', item_widget=None,
                 class_=None):
        """Initialize extended list widget."""
        assert html_tag in ('ol', 'ul', 'div', None)
        self.html_tag = html_tag
        self.class_ = class_
        if item_widget:
            self.item_widget = item_widget

    def open_tag(self, field, **kwargs):
        """Render open tag."""
        if self.html_tag:
            kwargs.setdefault('id', field.id)
            if self.class_:
                kwargs['class_'] = kwargs.get('class_', '') + ' ' + self.class_
            return '<%s %s>' % (self.html_tag, html_params(**kwargs))
        return ''

    def close_tag(self, field, **kwargs):
        """Render close tag."""
        if self.html_tag:
            return '</%s>' % self.html_tag
        return ''

    def item_kwargs(self, field, subfield):
        """Return keyword arguments for a field."""
        return {}

    def __call__(self, field, **kwargs):
        """Render extended list widget."""
        html = [self.open_tag(field, **kwargs)]
        hidden = []
        for subfield in field:
            if isinstance(subfield.widget, HiddenInput) or \
                    self.item_widget is None:
                hidden.append(subfield)
            else:
                html.append(
                    self.item_widget(subfield, **self.item_kwargs(field,
                                                                  subfield))
                )
        html.append(self.close_tag(field, **kwargs))
        # Add hidden fields in the end.
        for h in hidden:
            html.append(h())
        return HTMLString(''.join(html))


class DynamicListWidget(ExtendedListWidget):

    """Render a list of fields as a list of divs.

    Additionally adds:
    * A hidden input to keep track of the last index.
    * An 'add another' item button.

    Each subfield is rendered with DynamicItemWidget, which will add buttons
    for each item to sort and remove the item.
    """

    item_widget = DynamicItemWidget()
    icon_add = "fa fa-plus"

    def __init__(self, **kwargs):
        """Initialize dynamic list widget."""
        self.icon_add = kwargs.pop('icon_add', self.icon_add)
        self.item_widget = kwargs.pop('item_widget', self.item_widget)
        defaults = dict(
            html_tag='div',
            class_='dynamic-field-list',
        )
        defaults.update(kwargs)
        super(DynamicListWidget, self).__init__(**defaults)

    def _add_button(self, field):
        """Render add button."""
        label = getattr(field, 'add_label', None) or \
            "Add %s" % field.label.text
        ctx = {
            "label": label,
            "icon_add_class": self.icon_add
        }
        return render_macro_from_template(name="add_button",
                                          template="forms/macros.html",
                                          ctx=ctx)

    def item_kwargs(self, field, subfield):
        """Return keyword arguments for a field."""
        return {'empty_index': field.empty_index}

    def open_tag(self, field, **kwargs):
        """Render open tag."""
        html = super(DynamicListWidget, self).open_tag(field, **kwargs)
        html += """<input %s>""" % html_params(
            name=field.id + '-__last_index__',
            id=field.id + '-__last_index__',
            type="hidden",
            value=field.last_index,
        )
        return html

    def close_tag(self, field, **kwargs):
        """Render close tag."""
        html = self._add_button(field)
        html += super(DynamicListWidget, self).close_tag(field, **kwargs)
        return html


#
# Radio input widgets
#
class BigIconRadioInput(RadioInput):

    """Render a single radio button with icon.

    This widget is most commonly used in conjunction with InlineListWidget or
    some other listing, as a single radio button is not very useful.
    """

    input_type = 'radio'

    def __init__(self, icons={}, **kwargs):
        """Initialize radio input widget with big icon."""
        self.choices_icons = icons
        super(BigIconRadioInput, self).__init__(**kwargs)

    def __call__(self, field, **kwargs):
        """Render radio input."""
        if field.checked:
            kwargs['checked'] = u'checked'

        html = super(BigIconRadioInput, self).__call__(field, **kwargs)
        icon = self.choices_icons.get(field._value(), '')
        if icon:
            html = """<i class="%s"></i><br />%s</br>%s""" % (
                icon, field.label.text, html
            )
        return html
