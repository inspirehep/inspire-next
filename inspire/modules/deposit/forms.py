# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2014, 2015 CERN.
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
from wtforms.fields import DateTimeField, SubmitField
from flask.ext.wtf import Form

from invenio.base.i18n import _
from invenio.base.globals import cfg
from invenio.modules.deposit import fields
from invenio.modules.deposit.form import WebDepositForm
from invenio.modules.deposit.field_widgets import ColumnInput, \
    ExtendedListWidget, \
    ItemWidget, \
    DynamicListWidget, \
    DynamicItemWidget
from invenio.modules.deposit.autocomplete_utils import kb_dynamic_autocomplete
from invenio.modules.deposit.validation_utils import DOISyntaxValidator

from .fields import ArXivField
# from .fields import ISBNField
from .validators.dynamic_fields import AuthorsValidation
from .filters import clean_empty_list
from .validators.simple_fields import duplicated_doi_validator, \
    duplicated_arxiv_id_validator, arxiv_syntax_validation, \
    pdf_validator

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
            _('Import'))
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
        (_('Journal Information already exists'),
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


def defensedate_widget(field, **kwargs):
    """Date widget fot thesis."""
    field_id = kwargs.pop('id', field.id)
    html = [u'<div class="row %s"><div class="col-xs-12">\
            <input class="datepicker form-control" %s type="text">\
            </div></div>'
            % (THESIS_CLASS, html_params(id=field_id,
                                         name=field_id,
                                         value=field.data or ''))]
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
        autocomplete='affiliation',
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


class ReportNumberInlineForm(WebDepositForm):

    """Repor number inline form."""

    report_number = fields.TextField(
        label=_('Report Number'),
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


class LiteratureForm(WebDepositForm):

    """Literature form fields."""

    doi = fields.DOIField(
        label=_('DOI'),
        processors=[],
        export_key='doi',
        description='e.g. 10.1086/305772 or doi:10.1086/305772',
        placeholder='',
        validators=[DOISyntaxValidator("The provided DOI is invalid - it should look similar to '10.1086/305772'."),
                    duplicated_doi_validator],
    )

    arxiv_id = ArXivField(
        label=_('arXiv ID'),
        export_key="arxiv_id",
        validators=[arxiv_syntax_validation, duplicated_arxiv_id_validator],
    )

    categories_arXiv = fields.TextField(
        export_key='categories',
        widget=HiddenInput(),
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
        validators=[validators.DataRequired()],
    )

    title = fields.TitleField(
        label=_('Title'),
        widget_classes="form-control",
        validators=[validators.DataRequired()],
        export_key='title',
    )

    title_source = fields.TitleField(
        export_key='title_source',
        widget=HiddenInput(),
    )

    title_arXiv = fields.TitleField(
        export_key='title_arXiv',
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
        export_key="collaboration",
        widget_classes="form-control" + ARTICLE_CLASS
    )

    experiment = fields.TextField(
        placeholder=_("Start typing for suggestions"),
        export_key="experiment",
        label=_('Experiment'),
        widget_classes="form-control",
        autocomplete="experiment"
    )

    subject = fields.SelectMultipleField(
        label=_('Subject'),
        widget_classes="form-control",
        export_key='subject_term',
        filters=[clean_empty_list],
        validators=[validators.DataRequired()]
    )

    abstract = fields.TextAreaField(
        label=_('Abstract'),
        default='',
        widget_classes="form-control",
        export_key='abstract',
    )

    languages = [("en", _("English")),
                 ("rus", _("Russian")),
                 ("ger", _("German")),
                 ("fre", _("French")),
                 ("ita", _("Italian")),
                 ("spa", _("Spanish")),
                 ("chi", _("Chinese")),
                 ("por", _("Portuguese")),
                 ("oth", _("Other"))]

    language = fields.LanguageField(
        label=_("Language"),
        export_key="language",
        choices=languages
    )

    other_language = fields.TextField(
        label=_("Other Language"),
        export_key="other_language",
        widget_classes="form-control",
        description="What is the language of the publication?"
    )

    conf_name = fields.TextField(
        placeholder=_("Start typing for suggestions"),
        label=_('Conference Information'),
        description=_('Conference name, acronym, place, date'),
        widget_classes="form-control" + ARTICLE_CLASS,
        autocomplete='conference'
    )

    conference_id = fields.TextField(
        export_key='conference_id',
        widget=HiddenInput(),
    )

    license_url = fields.TextField(
        label=_('License URL'),
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
        add_label=_('Add another report number'),
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
        label=_('Supervisors'),
        add_label=_('Add another supervisor'),
        min_entries=1,
        widget_classes=THESIS_CLASS,
    )

    thesis_date = fields.Date(
        label=_('Date of Submission'),
        description='Format: YYYY-MM-DD.',
        widget=defensedate_widget,
    )

    defense_date = fields.Date(
        label=_('Date of Defense'),
        description='Format: YYYY-MM-DD.',
        widget=defensedate_widget,
    )

    degree_type = fields.SelectField(
        label=_('Degree Type'),
        widget_classes="form-control" + THESIS_CLASS,
    )

    institution = fields.TextField(
        autocomplete='affiliation',
        placeholder='Start typing for suggestions',
        label=_('Institution'),
        widget_classes="form-control" + THESIS_CLASS,
    )

    # license = fields.SelectField(
    #     label=_('License'),
    #     default='',
    #     widget_classes="form-control" + THESIS_CLASS,
    # )

    # ============
    # Journal Info
    # ============
    journal_title = fields.TextField(
        placeholder=_("Start typing for suggestions"),
        label=_('Journal Title'),
        widget_classes="form-control" + ARTICLE_CLASS,
        autocomplete_fn=kb_dynamic_autocomplete("dynamic_journal_titles",
                                             mapper=journal_title_kb_mapper)
    )

    page_range_article_id = fields.TextField(
        label=_('Page Range/Article ID'),
        description=_('e.g. 1-100'),
        widget_classes="form-control" + ARTICLE_CLASS
    )

    volume = fields.TextField(
        label=_('Volume'),
        widget_classes="form-control" + ARTICLE_CLASS
    )

    year = fields.TextField(
        label=_('Year'),
        widget_classes="form-control" + ARTICLE_CLASS
    )

    issue = fields.TextField(
        label=_('Issue'),
        widget_classes="form-control" + ARTICLE_CLASS
    )

    nonpublic_note = fields.TextAreaField(
        label=_('Proceedings'),
        description='Editors, title of proceedings, publisher, year of publication, page range, URL',
        widget=wrap_nonpublic_note,
        widget_classes="form-control" + ARTICLE_CLASS
    )

    note = fields.TextAreaField(
        widget=HiddenInput(),
        export_key='note',
    )

    # ============
    # References
    # ============

    references = fields.TextAreaField(
        label=_('References'),
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
    # file_field = fields.FileUploadField(
    #     label="",
    #     widget=plupload_widget,
    #     widget_classes="form-control" + THESIS_CLASS,
    #     export_key=False
    # )

    # url = fields.DynamicFieldList(
    #     fields.FormField(
    #         UrlInlineForm,
    #         widget=ExtendedListWidget(
    #             item_widget=ItemWidget(),
    #             html_tag='div',
    #         ),
    #     ),
    #     #validators=[validators.URL(), validators.Optional, ],
    #     label=_('If available, please provide us with an accessible URL for the pdf'),
    #     add_label=_('Add another url'),
    #     min_entries=1,
    #     export_key='url',
    #     widget_classes='',
    # )

    url = fields.TextField(
        label=_('Link to PDF'),
        description=_('Where can we find a PDF to check the references?'),
        placeholder='http://www.example.com/document.pdf',
        validators=[pdf_validator],
        widget_classes="form-control",
    )

    additional_url = fields.TextField(
        label=_('Link to additional information (e.g. abstract)'),
        description=_('Which page should we link from INSPIRE?'),
        placeholder='http://www.example.com/splash-page.html',
        # validators=[pdf_validator],
        widget_classes="form-control",
    )

    # ====================
    # Extra comments
    # ====================

    extra_comments = fields.TextAreaField(
        label=_('Comments'),
        description='Any extra comments related to your submission',
        widget_classes="form-control"
    )

    # ok_to_upload = fields.BooleanField(
    #     label="",
    #     default=False,
    #     widget=CheckboxButton(msg=_('I confirm I have read the License Agreement')),
    #     validators=[required_if_files('file_field',
    #                                   message=_("Please, check this box to upload material.")
    #                                   ),
    #                 ]
    #     )

    #
    # Form Configuration
    #
    _title = _("Suggest content")

    # Group fields in categories

    groups = [
        ('Import information',
            ['arxiv_id', 'doi', 'import_buttons']),
        ('Document Type',
            ['type_of_doc', ]),
        ('Links',
            ['url', 'additional_url']),
        ('Basic Information',
            ['title', 'title_arXiv', 'categories_arXiv', 'language',
             'other_language', 'title_translation', 'subject', 'authors',
             'collaboration', 'experiment', 'abstract', 'page_nr',
             'report_numbers']),
        ('Thesis Information',
            ['supervisors', 'defense_date', 'thesis_date', 'degree_type',
             'institution', 'license_url']),
        # ('Licenses and copyright',
        #     ['license', 'license_url'], {'classes': 'collapse'}),
        ('Journal Information',
            ['journal_title', 'volume', 'issue', 'year',
             'page_range_article_id']),
        ('Conference Information',
            ['conf_name', 'conference_id'], {'classes': 'collapse'}),
        ('Proceedings Information (if not published in a journal)',
            ['nonpublic_note'], {'classes': 'collapse'}),
        ('References',
            ['references'], {'classes': 'collapse'}),
        # ('Upload files',
        #     ['file_field', 'ok_to_upload']),
        ('Additional comments',
            ['extra_comments'], {'classes': 'collapse'}),
    ]

    field_sizes = {
        'type_of_doc': 'col-xs-12 col-md-3',
        'wrap_nonpublic_note': 'col-md-9',
        'degree_type': 'col-xs-12 col-md-3',
    }


    def __init__(self, *args, **kwargs):
        """Constructor."""
        super(LiteratureForm, self).__init__(*args, **kwargs)
        from invenio.modules.knowledge.api import get_kb_mappings
        self.subject.choices = [(x['value'], x['value'])
            for x in get_kb_mappings(cfg["DEPOSIT_INSPIRE_SUBJECTS_KB"])]
        self.degree_type.choices = [('', '')] + [(x['value'], x['value'])
            for x in get_kb_mappings(cfg["DEPOSIT_INSPIRE_DEGREE_KB"])]
        # self.license.choices = [('', '')] + [(x['key'], x['key'])
        #     for x in get_kb_mappings(cfg["DEPOSIT_INSPIRE_LICENSE_KB"])]


class FilterDateForm(Form):

    """Stats filter date form."""

    since_date = DateTimeField(
        label=_('From'),
        description='Format: YYYY-MM-DD.')
    until_date = DateTimeField(
        label=_('To'),
        description='Format: YYYY-MM-DD.')
    submit = SubmitField(_("Filter depositions"))
