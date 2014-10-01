# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2014 CERN.
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

"""Contains forms related to INSPIRE submission."""

from wtforms import validators
from wtforms.widgets import html_params, HTMLString, HiddenInput

from invenio.base.i18n import _
from invenio.base.globals import cfg
from invenio.modules.deposit import fields
from invenio.modules.deposit.form import WebDepositForm
from invenio.modules.deposit.field_widgets import plupload_widget, \
    ColumnInput, \
    ExtendedListWidget, \
    ItemWidget
from invenio.modules.deposit.autocomplete_utils import kb_dynamic_autocomplete
from invenio.modules.deposit.validation_utils import DOISyntaxValidator

from .fields import ArXivField
# from .fields import ISBNField
from .validators.dynamic_fields import AuthorsValidation
from .filters import clean_empty_list
from .validators.simple_fields import duplicated_doi_validator, \
    duplicated_arxiv_id_validator, arxiv_syntax_validation

#
# Field class names
#
ARTICLE_CLASS = " article-related"
THESIS_CLASS = " thesis-related"
CHAPTER_CLASS = " chapter-related"
BOOK_CLASS = " book-related"
PROCEEDINGS_CLASS = " proceedings-related"


#
# Custom field widgets
#
def importdata_button(field, **dummy_kwargs):
    """Import data button."""
    html = u'<button %s data-target="%s">%s</button>' % \
           (html_params(id="importData",
                        class_="btn btn-success btn-large",
                        name="importData",
                        type="button"),
            '#myModal',
            _('Auto import'))
    return HTMLString(html)


def skip_importdata(field, **dummy_kwargs):
    """Skip Import data button."""
    html = u'<button %s>%s</button>' % \
           (html_params(id="skipImportData",
                        class_="btn btn-link",
                        name="skipImportData",
                        type="button"),
            _('Skip, and fill the form manually'))
    return HTMLString(html)


#
# Group buttons of import and skip
#
def import_buttons_widget(field, **dummy_kwargs):
    """Buttons for import data and skip"""
    html_skip = skip_importdata(field)
    html_import = importdata_button(field)
    html = [u'<div class="pull-right">' + html_skip + html_import + u'</div>']
    return HTMLString(u''.join(html))


#
# Tooltips on disabled elements require wrapper elements
#
def wrap_nonpublic_note(field, **dummy_kwargs):
    """Proceedings box with tooltip."""
    html = u'<div class="tooltip-wrapper" data-toggle="tooltip"' \
        'title="%s"><textarea %s></textarea></div>' % \
        (_('Journal Information already exists'),
        html_params(id="nonpublic_note",
                    class_="form-control nonpublic_note",
                    name="nonpublic_note"))
    return HTMLString(html)


def radiochoice_buttons(field, **dummy_kwargs):
    """Radio choice buttons."""
    html = ''
    for choice, value in field.choices:
        html += u'<label class="btn btn-default"> \
                    <input type="radio" name="%s" id="%s"> \
                %s</label>' % (choice, choice, value)
    html = [u'<div class="btn-group" data-toggle="buttons">' + html + u'</div>']
    return HTMLString(u''.join(html))


def defensedate_widget(field, **kwargs):
    """Date widget fot thesis."""
    field_id = kwargs.pop('id', field.id)
    html = [u'<div class="row %s"><div class="col-xs-5 col-sm-3">\
            <input class="datepicker form-control" %s type="text">\
            </div></div'
            % (THESIS_CLASS, html_params(id=field_id,
                                         name=field_id,
                                         value=field.data or ''))]
    return HTMLString(u''.join(html))


def institutions_kb_mapper(val):
    """Return object ready to autocomplete affiliations."""
    return {
        'value': "%s" % val,
        'fields': {
            "affiliation": val,
        }
    }


def journal_title_kb_mapper(val):
    """Return object ready to autocomplete journal titles."""
    return {
        'value': "%s" % val,
        'fields': {
            "journal_title": val,
        }
    }


def experiment_kb_mapper(val):
    """Return object ready to autocomplete experiments."""
    return {
        'value': "%s" % val,
        'fields': {
            "experiment": val,
        }
    }


class AuthorInlineForm(WebDepositForm):

    """Author inline form."""

    name = fields.TextField(
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-6", description="Family name, First name"),
        # validators=[
        #     validators.Required(),
        # ],
        export_key='full_name',
    )
    affiliation = fields.TextField(
        autocomplete=kb_dynamic_autocomplete("InstitutionsCollection",
                                             mapper=institutions_kb_mapper),
        placeholder='Start typing for suggestions',
        autocomplete_limit=5,
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-4 col-pad-0", description="Affiliation"),
        export_key='affiliation',
    )


class UrlInlineForm(WebDepositForm):

    """Url inline form."""

    url = fields.TextField(
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-10"),
        export_key='full_url',
        placeholder='http://www.example.com',
    )


class LiteratureForm(WebDepositForm):

    """Literature form fields."""

    # captcha = RecaptchaField()

    doi = fields.DOIField(
        label=_('DOI'),
        processors=[],
        export_key='doi',
        description='e.g. 10.1234/foo.bar or doi:10.1234/foo.bar',
        placeholder='',
        validators=[DOISyntaxValidator(), duplicated_doi_validator],
    )

    arxiv_id = ArXivField(
        label=_('arXiv ID'),
        validators=[arxiv_syntax_validation, duplicated_arxiv_id_validator],
    )

    # isbn = ISBNField(
    #     label=_('ISBN'),
    #     widget_classes='form-control',
    # )

    import_buttons = fields.SubmitField(
        label=_(' '),
        widget=import_buttons_widget
    )

    types_of_doc = [("article", _("Article/Conference paper")),
                    ("thesis", _("Thesis"))]
                    # ("chapter", _("Book Chapter")),
                    # ("book", _("Book")),
                    # ("proceedings", _("Proceedings"))]

    type_of_doc = fields.SelectField(
        label='Type of Document',
        choices=types_of_doc,
        default="article",
        #widget=radiochoice_buttons,
        widget_classes='form-control',
        validators=[validators.Required()],
    )

    title = fields.TitleField(
        label=_('Title'),
        widget_classes="form-control",
        validators=[validators.Required()],
        export_key='title',
    )

    title_arXiv = fields.TitleField(
        export_key='title_arXiv',
        widget_classes="hidden",
        widget=HiddenInput(),
    )

    title_translation = fields.TitleField(
        label=_('Translated Title'),
        description='Original title translated to english language.',
        widget_classes="form-control",
        export_key='title_translation',
    )

    authors = fields.DynamicFieldList(
        fields.FormField(
            AuthorInlineForm,
            widget=ExtendedListWidget(
                item_widget=ItemWidget(),
                html_tag='div',
            ),
        ),
        label='Authors',
        add_label='Add another author',
        min_entries=1,
        widget_classes='',
        export_key='authors',
        validators=[AuthorsValidation],
    )

    collaboration = fields.TextField(
        label=_('Collaboration'),
        widget_classes="form-control"
    )

    experiment = fields.TextField(
        placeholder=_("Start typing for suggestions"),
        label=_('Experiment'),
        widget_classes="form-control",
        autocomplete=kb_dynamic_autocomplete("dynamic_experiments",
                                             mapper=experiment_kb_mapper)
    )

    # this should be a prefilled dropdown
    subject = fields.SelectMultipleField(
        label=_('Subject'),
        widget_classes="form-control",
        export_key='subject_term',
        filters=[clean_empty_list]
    )

    abstract = fields.TextAreaField(
        label=_('Abstract'),
        default='',
        widget_classes="form-control",
        export_key='abstract',
    )

    page_nr = fields.TextField(
        label=_('Number of Pages'),
        widget_classes="form-control",
        export_key='page_nr'
    )

    languages = [("en", _("English")),
                 ("fre", _("French")),
                 ("ger", _("German")),
                 ("dut", _("Dutch")),
                 ("ita", _("Italian")),
                 ("spa", _("Spanish")),
                 ("por", _("Portuguese")),
                 ("gre", _("Greek")),
                 ("slo", _("Slovak")),
                 ("cze", _("Czech")),
                 ("hun", _("Hungarian")),
                 ("pol", _("Polish")),
                 ("nor", _("Norwegian")),
                 ("swe", _("Swedish")),
                 ("fin", _("Finnish")),
                 ("rus", _("Russian")),
                 ("oth", _("Other"))]

    language = fields.LanguageField(
        label=_("Language"),
        choices=languages
    )

    conf_name = fields.TextField(
        placeholder=_("Start typing for suggestions"),
        label=_('Conference Information'),
        description=_('Conference name, acronym, place, date'),
        widget_classes="form-control"
    )

    conference_id = fields.TextField(
        export_key='conference_id',
        widget_classes="hidden",
        widget=HiddenInput(),
    )

    license_url = fields.TextField(
        label=_('License URL'),
        export_key='license_url',
        widget_classes="hidden",
        widget=HiddenInput(),
    )

    # ==============
    # Thesis related
    # ==============
    supervisors = fields.DynamicFieldList(
        fields.FormField(
            AuthorInlineForm,
            widget=ExtendedListWidget(
                item_widget=ItemWidget(),
                html_tag='div',
            ),
        ),
        label=_('Supervisors'),
        add_label=_('Add another supervisor'),
        min_entries=1,
        export_key='supervisors',
        widget_classes=THESIS_CLASS,
    )

    defense_date = fields.Date(
        label=_('Date of Defense'),
        description='Format: YYYY-MM-DD.',
        widget=defensedate_widget,
    )

    degree_type = fields.TextField(
        label=_('Degree type'),
        widget_classes="form-control" + THESIS_CLASS,
    )

    university = fields.TextField(
        label=_('University'),
        widget_classes="form-control" + THESIS_CLASS,
    )

    # ============
    # Journal Info
    # ============
    journal_title = fields.TextField(
        placeholder=_("Start typing for suggestions"),
        label=_('Journal Title'),
        widget_classes="form-control",
        autocomplete=kb_dynamic_autocomplete("dynamic_journal_titles",
                                             mapper=journal_title_kb_mapper)
    )

    page_range = fields.TextField(
        label=_('Page Range'),
        description=_('e.g. 1-100'),
        widget_classes="form-control"
    )

    article_id = fields.TextField(
        label=_('Article ID'),
        widget_classes="form-control"
    )

    volume = fields.TextField(
        label=_('Volume'),
        widget_classes="form-control"
    )

    year = fields.TextField(
        label=_('Year'),
        widget_classes="form-control"
    )

    issue = fields.TextField(
        label=_('Issue'),
        widget_classes="form-control"
    )

    nonpublic_note = fields.TextAreaField(
        label=_('Proceedings'),
        description='Editors, title of proceedings, publisher, year of publication, page range',
        widget=wrap_nonpublic_note
    )

    note = fields.TextAreaField(
        export_key='note',
        widget_classes="hidden",
        widget=HiddenInput(),
    )

    # ====================
    # Fulltext Information
    # ====================
    file_field = fields.FileUploadField(
        label="",
        widget=plupload_widget,
        export_key=False
    )

    url = fields.DynamicFieldList(
        fields.FormField(
            UrlInlineForm,
            widget=ExtendedListWidget(
                item_widget=ItemWidget(),
                html_tag='div',
            ),
        ),
        #validators=[validators.URL(), validators.Optional, ],
        label=_('External URL'),
        add_label=_('Add another url'),
        min_entries=1,
        export_key='url',
        widget_classes='',
    )

    # ok_to_upload = fields.BooleanField(
    #     label=_('I ensure the file is free to be uploaded.'),
    #     default=False,
    #     validators=[required_if('file_field',
    #                             [lambda x: bool(x.strip()), ],  # non-empty
    #                             message="It's required to check this box."
    #                             ),
    #                 required_if('url',
    #                             [lambda x: bool(x.strip()), ],  # non-empty
    #                             message="It's required to check this box."
    #                             ),
    #                 ]
    #     )

    #
    # Form Configuration
    #
    _title = _("Literature submission")

    # Group fields in categories

    groups = [
        ('Import from existing source',
            ['arxiv_id', 'doi', 'import_buttons']),
        ('Document Type',
            ['captcha', 'type_of_doc', ]),
        ('Basic Information',
            ['title', 'title_arXiv', 'language', 'title_translation', 'authors',
             'collaboration', 'experiment', 'abstract', 'page_nr', 'subject',
             'supervisors', 'defense_date', 'degree_type', 'university',
             'license_url']),
        ('Conference Information',
            ['conf_name', 'conference_id']),
        ('Journal Information',
            ['journal_title', 'volume', 'issue', 'page_range', 'article_id',
             'year']),
        ('Proceedings Information (not published in journal)',
            ['nonpublic_note', 'note']),
        ('Upload/link files',
            ['file_field', 'url']),
    ]

    field_sizes = {
        'file_field': 'col-md-12',
        'type_of_doc': 'col-xs-4',
        'wrap_nonpublic_note': 'col-md-9',
    }

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super(LiteratureForm, self).__init__(*args, **kwargs)
        from invenio.modules.knowledge.api import get_kb_mappings
        self.subject.choices = [(x['value'], x['value'])
            for x in get_kb_mappings(cfg["DEPOSIT_INSPIRE_SUBJECTS_KB"])]
