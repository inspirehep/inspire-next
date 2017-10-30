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

"""Contains forms related to INSPIRE Literature suggestion."""

from __future__ import absolute_import, division, print_function

from babel import Locale
from wtforms import validators
from wtforms.widgets import HiddenInput, HTMLString, html_params

from inspire_schemas.api import load_schema
from inspirehep.modules.forms import fields
from inspirehep.modules.forms.field_widgets import (
    ColumnInput,
    DynamicListWidget,
    DynamicItemWidget,
    ExtendedListWidget,
    ItemWidget,
)
from inspirehep.modules.forms.filter_utils import clean_empty_list
from inspirehep.modules.forms.form import INSPIREForm
from inspirehep.modules.forms.validation_utils import DOISyntaxValidator
from inspirehep.modules.forms.validators.dynamic_fields import (
    AuthorsValidation,
)
from inspirehep.modules.forms.validators.simple_fields import (
    arxiv_syntax_validation,
    arxiv_id_already_pending_in_holdingpen_validator,
    date_validator,
    doi_already_pending_in_holdingpen_validator,
    duplicated_arxiv_id_validator,
    duplicated_doi_validator,
    no_pdf_validator,
    pdf_validator,
    year_validator,
)


#
# Field class names
#

ARTICLE_CLASS = " article-related"
THESIS_CLASS = " thesis-related"
CHAPTER_CLASS = " chapter-related"
BOOK_CLASS = " book-related"
PROCEEDINGS_CLASS = " proceedings-related"

FORM_LANGUAGES = ['en', 'ru', 'de', 'fr', 'it', 'es', 'zh', 'pt', 'ja']


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
            'Import')
    return HTMLString(html)


def skip_importdata(field, **dummy_kwargs):
    """Skip Import data button."""
    html = u'<button %s>%s</button>' % \
           (html_params(id="skipImportData",
                        class_="btn btn-link",
                        name="skipImportData",
                        type="button"),
            'Skip, and fill the form manually')
    return HTMLString(html)


#
# Group buttons of import and skip
#

def import_buttons_widget(field, **dummy_kwargs):
    """Button for import data and skip."""
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
        ('Journal Information already exists',
         html_params(id="nonpublic_note",
                     class_="form-control nonpublic_note" + ARTICLE_CLASS,
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


class CheckboxButton(object):

    """Checkbox button."""

    def __init__(self, msg=""):
        """Initialize widget with custom template."""
        self.msg = msg

    def __call__(self, field, **kwargs):
        """Render PLUpload widget."""
        html = '<div id="field-{0}">' \
               '<label for="{0}">' \
               '<input class="checkbox-ok-upload" name="{0}" type="checkbox" value="{2}">' \
               '<strong><em>{1}</em></strong><small>&nbsp;(temporary text)</small>' \
               '</label>' \
               '</div>'.format(field.id,
                               self.msg,
                               field.default)
        return HTMLString(html)


def journal_title_kb_mapper(val):
    """Return object ready to autocomplete journal titles."""
    return {
        'value': "%s" % val,
        'fields': {
            "journal_title": val,
        }
    }


class AuthorInlineForm(INSPIREForm):

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
        autocomplete='affiliation',
        placeholder='Start typing for suggestions',
        autocomplete_limit=5,
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-4 col-pad-0", description="Affiliation"),
        export_key='affiliation',
    )


class UrlInlineForm(INSPIREForm):

    """Url inline form."""

    url = fields.TextField(
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-10"),
        export_key='full_url',
        placeholder='http://www.example.com',
    )


class ReportNumberInlineForm(INSPIREForm):

    """Repor number inline form."""

    report_number = fields.TextField(
        label='Report Number',
        widget=ColumnInput(class_="col-xs-10"),
        widget_classes="form-control"
    )


class UnsortedDynamicListWidget(DynamicListWidget):
    def __init__(self, **kwargs):
        self.item_widget = UnorderedDynamicItemWidget()
        super(UnsortedDynamicListWidget, self).__init__(**kwargs)


class UnorderedDynamicItemWidget(DynamicItemWidget):
    def _sort_button(self):
        return ""


class LiteratureForm(INSPIREForm):

    """Literature form fields."""

    doi = fields.DOIField(
        label='DOI',
        processors=[],
        export_key='doi',
        description='e.g. 10.1086/305772 or doi:10.1086/305772',
        placeholder='',
        validators=[
            DOISyntaxValidator(
                "The provided DOI is invalid - it should look similar to "
                "'10.1086/305772'."
            ),
            duplicated_doi_validator,
            doi_already_pending_in_holdingpen_validator,
        ],
    )

    arxiv_id = fields.ArXivField(
        label='arXiv ID',
        export_key="arxiv_id",
        validators=[
            arxiv_syntax_validation,
            duplicated_arxiv_id_validator,
            arxiv_id_already_pending_in_holdingpen_validator,
        ],
    )

    categories_arXiv = fields.TextField(
        widget=HiddenInput(),
        export_key='categories',
    )

    import_buttons = fields.SubmitField(
        label=' ',
        widget=import_buttons_widget
    )

    types_of_doc = [("article", "Article/Conference paper"),
                    ("thesis", "Thesis"),
                    ('book', 'Book'),
                    ('chapter', 'Book chapter')]
    # ("proceedings", _("Proceedings"))

    type_of_doc = fields.SelectField(
        label='Type of Document',
        choices=types_of_doc,
        default="article",
        # widget=radiochoice_buttons,
        widget_classes='form-control',
        validators=[validators.DataRequired()],
    )

    title = fields.TitleField(
        label='Title',
        widget_classes="form-control",
        validators=[validators.DataRequired()],
        export_key='title',
    )

    title_crossref = fields.TitleField(
        export_key='title_crossref',
        widget=HiddenInput(),
    )

    title_arXiv = fields.TitleField(
        export_key='title_arXiv',
        widget=HiddenInput(),
    )

    title_translation = fields.TitleField(
        label='Translated Title',
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
        label='Collaboration',
        export_key="collaboration",
        widget_classes="form-control" + ARTICLE_CLASS
    )

    experiment = fields.TextField(
        placeholder="Start typing for suggestions",
        export_key="experiment",
        label='Experiment',
        widget_classes="form-control",
        autocomplete="experiment"
    )

    subject = fields.SelectMultipleField(
        label='Subject',
        widget_classes="form-control",
        export_key='subject_term',
        filters=[clean_empty_list],
        validators=[validators.DataRequired()]
    )

    abstract = fields.TextAreaField(
        label='Abstract',
        default='',
        widget_classes="form-control",
        export_key='abstract',
    )

    language_choices = [
        (language, Locale('en').languages.get(language))
        for language in FORM_LANGUAGES
    ]
    language_choices.sort(key=lambda x: x[1])
    language_choices.append(
        ('oth', 'Other')
    )

    language = fields.LanguageField(
        label="Language",
        export_key="language",
        default="en",
        choices=language_choices
    )

    def _is_other_language(language):
        return language[0] not in FORM_LANGUAGES and len(language[0]) == 2

    other_language_choices = filter(
        _is_other_language,
        Locale('en').languages.items()
    )
    other_language_choices.sort(key=lambda x: x[1])

    other_language = fields.LanguageField(
        label="Other Language",
        export_key="other_language",
        widget_classes="form-control",
        choices=other_language_choices,
        description="What is the language of the publication?"
    )

    conf_name = fields.TextField(
        placeholder="Start typing for suggestions",
        label='Conference Information',
        description='Conference name, acronym, place, date',
        widget_classes="form-control" + ARTICLE_CLASS,
        autocomplete='conference'
    )

    conference_id = fields.TextField(
        export_key='conference_id',
        widget=HiddenInput(),
    )

    license_url = fields.TextField(
        label='License URL',
        export_key='license_url',
        widget=HiddenInput(),
    )

    report_numbers = fields.DynamicFieldList(
        fields.FormField(
            ReportNumberInlineForm,
            widget=ExtendedListWidget(
                item_widget=ItemWidget(),
                html_tag='div',
            ),
        ),
        add_label='Add another report number',
        min_entries=1,
        widget_classes='',
        widget=UnsortedDynamicListWidget(),
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
        label='Supervisors',
        add_label='Add another supervisor',
        min_entries=1,
        widget_classes=THESIS_CLASS,
    )

    thesis_date = fields.TextField(
        label='Date of Submission',
        description='Format: YYYY-MM-DD, YYYY-MM or YYYY.',
        validators=[date_validator],
        widget_classes='form-control' + THESIS_CLASS,
    )

    defense_date = fields.TextField(
        label='Date of Defense',
        description='Format: YYYY-MM-DD, YYYY-MM or YYYY.',
        validators=[date_validator],
        widget_classes='form-control' + THESIS_CLASS,
    )

    degree_type = fields.SelectField(
        label='Degree Type',
        default='phd',
        widget_classes="form-control" + THESIS_CLASS,
    )

    institution = fields.TextField(
        autocomplete='affiliation',
        placeholder='Start typing for suggestions',
        label='Institution',
        widget_classes="form-control" + THESIS_CLASS,
    )

    # =========
    # Book Info
    # =========

    publisher_name = fields.TextField(
        label='Publisher',
        widget_classes="form-control" + BOOK_CLASS,
    )

    publication_place = fields.TextField(
        label='Publication Place',
        widget_classes="form-control" + BOOK_CLASS,
    )

    series_title = fields.TextField(
        label='Series Title',
        widget_classes="form-control" + BOOK_CLASS,
        autocomplete='journal'
    )

    series_volume = fields.TextField(
        label='Volume',
        widget_classes="form-control" + BOOK_CLASS,
    )

    publication_date = fields.TextField(
        label='Publication Date',
        description='Format: YYYY-MM-DD, YYYY-MM or YYYY.',
        widget_classes="form-control" + BOOK_CLASS,
        validators=[date_validator],
    )

    # =================
    # Book Chapter Info
    # =================

    book_title = fields.TextField(
        label='Book Title',
        widget_classes="form-control" + CHAPTER_CLASS,
    )

    start_page = fields.TextField(
        placeholder='Start page of the chapter',
        widget_classes="form-control" + CHAPTER_CLASS,
    )

    end_page = fields.TextField(
        placeholder='End page of the chapter',
        widget_classes="form-control" + CHAPTER_CLASS,
    )

    find_book = fields.TextField(
        placeholder="Start typing for suggestions",
        label='Find Book',
        description='Book name, ISBN, Publisher',
        widget_classes="form-control" + CHAPTER_CLASS,
    )
    parent_book = fields.TextField(
        widget=HiddenInput(),
    )

    # ============
    # Journal Info
    # ============

    journal_title = fields.TextField(
        placeholder="Start typing for suggestions",
        label='Journal Title',
        widget_classes="form-control" + ARTICLE_CLASS,
        autocomplete='journal'
    )

    page_range_article_id = fields.TextField(
        label='Page Range/Article ID',
        description='e.g. 1-100',
        widget_classes="form-control" + ARTICLE_CLASS
    )

    volume = fields.TextField(
        label='Volume',
        widget_classes="form-control" + ARTICLE_CLASS
    )

    year = fields.TextField(
        label='Year',
        widget_classes="form-control" + ARTICLE_CLASS,
        validators=[year_validator],
    )

    issue = fields.TextField(
        label='Issue',
        widget_classes="form-control" + ARTICLE_CLASS
    )

    nonpublic_note = fields.TextAreaField(
        label='Proceedings',
        description='Editors, title of proceedings, publisher, year of publication, page range, URL',
        widget=wrap_nonpublic_note,
        widget_classes="form-control" + ARTICLE_CLASS
    )

    note = fields.TextAreaField(
        widget=HiddenInput(),
        export_key='note',
    )

    # ==========
    # References
    # ==========

    references = fields.TextAreaField(
        label='References',
        description='Please paste the references in plain text',
        widget_classes="form-control"
    )

    # ====================
    # Preprint Information
    # ====================

    preprint_created = fields.TextField(
        widget=HiddenInput(),
        export_key='preprint_created',
    )

    # ====================
    # Fulltext Information
    # ====================

    url = fields.TextField(
        label='Link to PDF',
        description='Where can we find a PDF to check the references?',
        placeholder='http://www.example.com/document.pdf',
        validators=[pdf_validator],
        widget_classes="form-control",
    )

    additional_url = fields.TextField(
        label='Link to additional information (e.g. abstract)',
        description='Which page should we link from INSPIRE?',
        placeholder='http://www.example.com/splash-page.html',
        validators=[no_pdf_validator],
        widget_classes="form-control",
    )

    # ==============
    # Extra comments
    # ==============

    extra_comments = fields.TextAreaField(
        label='Comments',
        description='Any extra comments related to your submission',
        widget_classes="form-control"
    )

    #
    # Form Configuration
    #
    _title = "Suggest content"

    # Group fields in categories

    groups = [
        ('Import information',
            ['arxiv_id', 'doi', 'import_buttons']),
        ('Document Type',
            ['type_of_doc', ]),
        ('Links',
            ['url', 'additional_url']),
        ('Publication Information',
            ['find_book', 'parent_book', 'book_title', 'start_page', 'end_page']),
        ('Basic Information',
            ['title', 'title_arXiv', 'categories_arXiv', 'language',
             'other_language', 'title_translation', 'subject', 'authors',
             'collaboration', 'experiment', 'abstract',
             'report_numbers']),
        ('Thesis Information',
            ['degree_type', 'thesis_date', 'defense_date', 'institution',
             'supervisors', 'license_url']),
        ('Publication Information',
            ['journal_title', 'volume', 'issue',
             'year', 'page_range_article_id']),
        ('Publication Information',
            ['series_title', 'series_volume', 'publication_date',
             'publisher_name', 'publication_place']),
        ('Conference Information',
            ['conf_name', 'conference_id'], {'classes': 'collapse'}),
        ('Proceedings Information (if not published in a journal)',
            ['nonpublic_note'], {'classes': 'collapse'}),
        ('References',
            ['references'], {'classes': 'collapse'}),
        ('Additional comments',
            ['extra_comments'], {'classes': 'collapse'}),
    ]

    field_sizes = {
        'type_of_doc': 'col-xs-12 col-md-3',
        'wrap_nonpublic_note': 'col-md-9',
        'publisher_name': 'col-xs-12 col-md-9',
        'publication_date': 'col-xs-12 col-md-4',
        'thesis_date': 'col-xs-12 col-md-4',
        'defense_date': 'col-xs-12 col-md-4',
        'degree_type': 'col-xs-12 col-md-3',
        'start_page': 'col-xs-12 col-md-3',
        'end_page': 'col-xs-12 col-md-3',
    }

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super(LiteratureForm, self).__init__(*args, **kwargs)

        inspire_categories_schema = load_schema('elements/inspire_field.json')
        categories = inspire_categories_schema['properties']['term']['enum']
        self.subject.choices = [(val, val) for val in categories]

        degree_type_schema = load_schema('elements/degree_type.json')
        degree_choices = [
            (val, val.capitalize()) if val != 'phd' else ('phd', 'PhD')
            for val in degree_type_schema['enum']
        ]
        degree_choices.sort(key=lambda x: x[1])
        self.degree_type.choices = degree_choices
