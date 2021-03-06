# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2018 CERN.
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

from wtforms import validators
from wtforms.fields import Flags
from wtforms.widgets import (
    HTMLString,
    HiddenInput,
    Select,
    TextInput,
    html_params,
)

from inspire_schemas.api import load_schema
from inspirehep.modules.forms.field_widgets import (
    ColumnInput,
    DynamicItemWidget,
    DynamicListWidget,
    ExtendedListWidget,
    ItemWidget,
    WrappedInput,
)
from inspirehep.modules.forms.form import INSPIREForm
from inspirehep.modules.forms import fields
from inspirehep.modules.forms.filter_utils import clean_empty_list
from inspirehep.modules.forms.validators.simple_fields import (
    duplicated_orcid_validator,
)
from inspirehep.modules.forms.validators.dynamic_fields import LessThan
from inspirehep.modules.forms.validation_utils import (
    ORCIDValidator,
    RegexpStopValidator,
)


def currentCheckboxWidget(field, **kwargs):
    """Current institution checkbox widget."""
    field_id = kwargs.pop('id', field.id)
    html = [u'<div class="col-md-10 col-margin-top pull-left">\
            <input %s %s type="checkbox">\
            <label for=%s>Current</label></div>'
            % (html_params(id=field_id,
                           name=field_id),
               field.data and "checked" or "",
               field_id)]
    return HTMLString(u''.join(html))


class WrappedSelect(Select):

    """Widget to wrap select input in further markup."""

    wrapper = '<div>%(field)s</div>'
    wrapped_widget = Select()

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


class ColumnSelect(WrappedSelect):

    """Specialized column wrapped input."""

    @property
    def wrapper(self):
        """Wrapper template with description support."""
        if 'description' in self.wrapper_args:
            return ('<div class="%(class_)s">%(field)s'
                    '<p class="text-muted field-desc">'
                    '<small>%(description)s</small></p></div>')
        return '<div class="%(class_)s">%(field)s</div>'


class InstitutionInlineForm(INSPIREForm):

    """Institution inline form."""

    rank_options = [
        ("rank", "Rank"),
        ("SENIOR", "Senior (permanent)"),
        ("JUNIOR", "Junior (leads to Senior)"),
        ("STAFF", "Staff (non-research)"),
        ("VISITOR", "Visitor"),
        ("PD", "PostDoc"),
        ("PHD", "PhD"),
        ("MASTER", "Master"),
        ("UNDERGRADUATE", "Undergrad"),
        ("OTHER", "Other"),
    ]

    name = fields.StringField(
        widget_classes='form-control',
        widget=ColumnInput(class_="col-md-6"),
        autocomplete='affiliation',
        placeholder="Institution. Type for suggestions",
    )

    rank = fields.SelectField(
        choices=rank_options,
        default="rank",
        widget=ColumnSelect(class_="col-md-6"),
        widget_classes='form-control',
        validators=[validators.DataRequired()],
    )

    start_year = fields.StringField(
        placeholder='Start Year',
        description=u'Format: YYYY.',
        widget=WrappedInput(
            wrapped_widget=TextInput(),
            wrapper='<div class="col-md-6 col-margin-top">%(field)s</div>'
        ),
        validators=[
            LessThan('end_year', message='Start year should be earlier than End year'),
            RegexpStopValidator(
                r'^(\d{4})?$',
                message='{} is not a valid year. Please use <i>yyyy</i> format.',
            ),
        ],
        widget_classes="form-control"
    )

    end_year = fields.StringField(
        placeholder='End Year',
        description=u'Format: YYYY.',
        widget=WrappedInput(
            wrapped_widget=TextInput(),
            wrapper='<div class="col-md-6 col-margin-top">%(field)s</div>'
        ),
        validators=[RegexpStopValidator(
            "^(\d{4})?$",
            message="{} is not a valid year. Please use <i>yyyy</i> format."
        )],
        widget_classes="form-control"
    )

    current = fields.BooleanField(
        widget=currentCheckboxWidget
    )

    emails = fields.FieldList(
        fields.HiddenField(label=''),
        widget_classes='hidden-list'
    )

    old_emails = fields.FieldList(
        fields.HiddenField(label=''),
        widget_classes='hidden-list'
    )


class EmailInlineForm(INSPIREForm):

    """Public emails inline form."""

    email = fields.StringField(
        widget_classes="form-control",
        validators=[validators.Optional(), validators.Email()],
    )

    original_email = fields.HiddenField()


class ExperimentsInlineForm(INSPIREForm):

    """Experiments inline form."""

    name = fields.StringField(
        placeholder="Experiment. Type for suggestions",
        label='Experiment',
        widget=ColumnInput(class_="col-md-6"),
        widget_classes="form-control",
        autocomplete="experiment"
    )

    start_year = fields.StringField(
        placeholder='Start Year',
        description=u'Format: YYYY.',
        widget=WrappedInput(
            wrapped_widget=TextInput(),
            wrapper='<div class="col-md-6">%(field)s</div>',
        ),
        validators=[
            LessThan('end_year', message='Start year should be earlier than End year'),
            RegexpStopValidator(
                r'^(\d{4})?$',
                message='{} is not a valid year. Please use <i>yyyy</i> format.',
            ),
        ],
        widget_classes="form-control"
    )

    end_year = fields.StringField(
        placeholder='End Year',
        description=u'Format: YYYY.',
        widget=WrappedInput(
            wrapped_widget=TextInput(),
            wrapper='<div class="col-md-6 col-margin-top">%(field)s</div>'
        ),
        validators=[
            RegexpStopValidator(
                r'^(\d{4})?$',
                message='{} is not a valid year. Please use <i>yyyy</i> format.',
            ),
        ],
        widget_classes="form-control"
    )

    current = fields.BooleanField(
        widget=currentCheckboxWidget
    )


class AdvisorsInlineForm(INSPIREForm):

    """Advisors inline form."""

    name = fields.TextField(
        widget_classes='form-control',
        placeholder="Name. Type for suggestions",
        autocomplete='author',
        widget=ColumnInput(
            class_="col-xs-5", description=u"Family name, First name"),
        export_key='full_name',
    )

    degree_types_schema = load_schema('elements/degree_type.json')
    degree_type_options = [
        (val, val.capitalize())
        for val in degree_types_schema['enum']
    ]
    degree_type_options.sort(key=lambda x: x[1])
    degree_type = fields.SelectField(
        choices=degree_type_options,
        label='Degree Type',
        widget_classes="form-control",
        default="phd",
        widget=ColumnSelect(class_="col-xs-5", description=u"Degree Type"),
    )


class WebpageInlineForm(INSPIREForm):

    """URL inline form."""

    webpage = fields.StringField(
        label='Your Webpage',
        placeholder='http://www.example.com',
        widget=ColumnInput(class_="col-xs-10"),
        widget_classes="form-control",
        validators=[validators.URL(), validators.Optional()]
    )


class DynamicUnsortedItemWidget(DynamicItemWidget):

    def _sort_button(self):
        return ""


class DynamicUnsortedWidget(DynamicListWidget):

    def __init__(self, **kwargs):
        """Initialize dynamic list widget."""
        self.item_widget = DynamicUnsortedItemWidget()
        super(DynamicUnsortedWidget, self).__init__(**kwargs)


class DynamicUnsortedNonRemoveItemWidget(DynamicItemWidget):

    def _sort_button(self):
        return ""

    def _remove_button(self):
        return ""


class DynamicUnsortedNonRemoveWidget(DynamicListWidget):

    def __init__(self, **kwargs):
        """Initialize dynamic list widget."""
        self.item_widget = DynamicUnsortedNonRemoveItemWidget()
        super(DynamicUnsortedNonRemoveWidget, self).__init__(**kwargs)


class AuthorUpdateForm(INSPIREForm):

    """Author update form."""

    bai = fields.StringField(
        label='Bai',
        description=u'e.g. M.Santos.1',
        widget=HiddenInput(),
        widget_classes="form-control",
        validators=[validators.Optional(),
                    RegexpStopValidator(
                        "(\\w+\\.)+\\d+",
                        message="A valid Bai is in the form of 'M.Santos.1'.",
        )]
    )

    inspireid = fields.StringField(
        label='Inspireid',
        description=u'e.g. INSPIRE-12345678',
        widget=HiddenInput(),
        widget_classes="form-control",
        validators=[validators.Optional(),
                    RegexpStopValidator(
                        r"^INSPIRE-\d{8}(?<!00000000)$",
                        message="A valid Inspireid is in the form of 'INSPIRE-12345678'.",
        )]
    )

    # Hidden field to hold record id information
    control_number = fields.IntegerField(
        widget=HiddenInput(),
        validators=[validators.Optional()],
    )

    given_names = fields.StringField(
        label='Given Names',
        description=u'e.g. Diego',
        validators=[validators.DataRequired()],
        widget_classes="form-control"
    )

    family_name = fields.StringField(
        label='Family Name',
        description=u'e.g. Martínez Santos',
        widget_classes="form-control"
    )

    display_name = fields.StringField(
        label='Display Name',
        description=u'How should the author be addressed throughout the site? e.g. Diego Martínez',
        validators=[validators.DataRequired()],
        widget_classes="form-control"
    )

    native_name = fields.StringField(
        label='Native Name',
        description=u'For non-Latin names e.g. 麦迪娜 or Эдгар Бугаев',
        widget_classes="form-control"
    )

    public_emails = fields.DynamicFieldList(
        fields.FormField(
            EmailInlineForm,
            widget=ExtendedListWidget(
                item_widget=ItemWidget(),
                html_tag='div',
            ),
            widget_classes="col-xs-10"
        ),
        description=u"This emails will be displayed online in the INSPIRE Author Profile.",
        label='Public emails',
        add_label='Add another email',
        min_entries=1,
        widget=DynamicUnsortedNonRemoveWidget(),
        widget_classes="ui-disable-sort"
    )

    orcid = fields.StringField(
        label='ORCID <img src="/oldui/images/orcid_icon_24.png" style="height:20px">',
        widget_classes="form-control",
        description=u"""ORCID provides a persistent digital identifier that distinguishes you from other researchers. Learn more at <a href="http://orcid.org" tabIndex="-1" target="_blank">orcid.org</a>""",
        widget=WrappedInput(wrapper="""
        <div class="input-group">
        <span class="input-group-addon" id="sizing-addon2">orcid.org/</span>
        %(field)s
        </div>
        """),
        placeholder="0000-0000-0000-0000",
        validators=[validators.Optional(),
                    RegexpStopValidator(
                        "\d{4}-\d{4}-\d{4}-\d{3}[\dX]",
                        message="A valid ORCID iD consists of 16 digits separated by dashes.",
        ),
            ORCIDValidator,
            duplicated_orcid_validator]
    )

    status_options = [("active", "Active"),
                      ("retired", "Retired"),
                      ("departed", "Departed"),
                      ("deceased", "Deceased")]

    status = fields.SelectField(
        label='Status',
        choices=status_options,
        default="active",
        validators=[validators.DataRequired()],
        widget_classes='form-control',
    )

    blog_url = fields.StringField(
        label='Blog',
        placeholder='http://www.example.com',
        icon="fa fa-wordpress",
        widget_classes="form-control",
        validators=[validators.URL(), validators.Optional()]
    )

    twitter_url = fields.StringField(
        label='Twitter',
        placeholder='https://twitter.com/inspirehep',
        icon="fa fa-twitter",
        widget_classes="form-control",
        validators=[validators.URL(), validators.Optional()]
    )

    linkedin_url = fields.StringField(
        label='Linkedin',
        placeholder='https://www.linkedin.com/pub/john-francis-lampen/16/750/778',
        icon="fa fa-linkedin-square",
        widget_classes="form-control",
        validators=[validators.URL(), validators.Optional()]
    )

    websites = fields.DynamicFieldList(
        fields.FormField(
            WebpageInlineForm,
            widget=ExtendedListWidget(
                item_widget=ItemWidget(),
                html_tag='div',
            ),
        ),
        add_label='Add another website',
        min_entries=1,
        widget_classes='ui-disable-sort',
        icon="fa fa-globe",
        widget=DynamicUnsortedWidget()
    )

    arxiv_categories_schema = load_schema('elements/arxiv_categories.json')
    research_field_options = [
        (val, val)
        for val in arxiv_categories_schema['enum']
        if '.' not in val or
        val in ('physics.ins-det', 'physics.acc-ph', 'physics.data-an')
    ]

    research_field = fields.SelectMultipleField(
        label='Field of Research',
        choices=research_field_options,
        widget_classes="form-control",
        filters=[clean_empty_list],
        validators=[validators.DataRequired()]
    )

    institution_history = fields.DynamicFieldList(
        fields.FormField(
            InstitutionInlineForm,
            widget=ExtendedListWidget(
                item_widget=ItemWidget(),
                html_tag='div',
            ),
            widget_classes="col-xs-10"
        ),
        label='Institution History',
        add_label='Add another institution',
        min_entries=1,
        widget=DynamicUnsortedWidget(),
        widget_classes="ui-disable-sort"
    )

    advisors = fields.DynamicFieldList(
        fields.FormField(
            AdvisorsInlineForm,
            widget=ExtendedListWidget(
                item_widget=ItemWidget(),
                html_tag='div',
            ),
        ),
        label='Advisors',
        add_label='Add another advisor',
        min_entries=1,
        widget=DynamicUnsortedWidget(),
        widget_classes="ui-disable-sort"
    )

    experiments = fields.DynamicFieldList(
        fields.FormField(
            ExperimentsInlineForm,
            widget=ExtendedListWidget(
                item_widget=ItemWidget(),
                html_tag='div',
            ),
            widget_classes="col-xs-10"
        ),
        label='Experiment History',
        add_label='Add another experiment',
        min_entries=1,
        widget=DynamicUnsortedWidget(),
        widget_classes="ui-disable-sort"
    )

    extra_comments = fields.TextAreaField(
        label='Comments',
        description=u'Send us any comments you might have. They will not be visible.',
        widget_classes="form-control"
    )

    #
    # Form Configuration
    #
    _title = "Update author details"

    # Group fields in categories

    groups = [
        ('Personal Information',
            ['given_names', 'family_name', 'display_name', 'native_name', 'email',
             'public_emails', 'status', 'orcid', 'bai', 'inspireid'],
            {"icon": "fa fa-user"}
         ),
        ('Personal Websites',
            ['websites', 'linkedin_url', 'blog_url',
                'twitter_url', "twitter_hidden"],
            {"icon": "fa fa-globe"}

         ),
        ('Career Information',
            ['research_field', 'institution_history',
                'experiments', 'advisors'],
            {"icon": "fa fa-university"}
         ),
        ('Comments',
            ['extra_comments'],
            {"icon": "fa fa-comments"}
         )
    ]

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super(AuthorUpdateForm, self).__init__(*args, **kwargs)
        is_review = kwargs.pop('is_review', False)
        is_update = kwargs.pop('is_update', False)

        if is_update:
            # remove validation for duplicate ORCIDs on update
            self.orcid.validators = self.orcid.validators[:-1]

        if is_review:
            self.bai.widget = TextInput()
            self.bai.flags = Flags()
            self.inspireid.widget = TextInput()
            self.inspireid.flags = Flags()
