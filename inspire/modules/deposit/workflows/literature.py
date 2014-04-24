#
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

from wtforms import validators
from lxml.html import fromstring
from wtforms.widgets import html_params, HTMLString

from invenio.modules.deposit.types import SimpleRecordDeposition
from invenio.modules.deposit.form import WebDepositForm
from invenio.base.i18n import _
from invenio.modules.deposit import fields
from invenio.modules.deposit.field_widgets import plupload_widget, \
    ColumnInput, \
    ExtendedListWidget, \
    ItemWidget
from invenio.modules.deposit.tasks import render_form, \
    create_recid, \
    prepare_sip, \
    finalize_record_sip, \
    upload_record_sip, \
    prefill_draft, \
    process_sip_metadata, \
    hold_for_approval
from invenio.modules.deposit.fields.doi import missing_doi_warning
from inspire.modules.deposit import fields as inspire_fields


#
# Helpers
#
def filter_empty_helper(keys=None):
    """Remove empty elements from a list."""
    def _inner(elem):
        if isinstance(elem, dict):
            for k, v in elem.items():
                if (keys is None or k in keys) and v:
                    return True
            return False
        else:
            return bool(elem)
    return _inner


#
# Field class names
#
article_class = " article-related"
thesis_class = " thesis-related"
chapter_class = " chapter-related"
book_class = " book-related"
proceedings_class = " proceedings-related"


#
# Custom field widgets
#
def radiochoice_buttons(field, **dummy_kwargs):
    """Radio choice buttons."""
    html = ''
    for choice, value in field.choices:
        html += u'<label class="btn btn-default"> \
                    <input type="radio" name="%s" id="%s"> \
                %s</label>' % (choice, choice, value)
    html = [u'<div class="btn-group" data-toggle="buttons">' + html + u'</div>']
    return HTMLString(u''.join(html))


def importdata_button(field, **dummy_kwargs):
    """Import data button."""
    html = u'<button %s data-loading-text="%s" %s>%s</button>' % \
           (html_params(style="float:right; width: 160px;",
                        id="importData",
                        class_="btn btn-primary btn-large",
                        name="importData",
                        type="button"),
            _('Importing data...'),
            'data-toggle="modal" data-target="#modal-message"',
            field.label.text)
    return HTMLString(html)


def defensedate_widget(field, **kwargs):
    """Date widget fot thesis."""
    field_id = kwargs.pop('id', field.id)
    html = [u'<div class="row %s"><div class="col-xs-5 col-sm-3">\
            <input class="datepicker form-control" %s type="text">\
            </div></div'
            % (thesis_class, html_params(id=field_id,
                                         name=field_id,
                                         value=field.data or ''))]
    return HTMLString(u''.join(html))


#
# Forms
#
class AuthorInlineForm(WebDepositForm):

    """Author inline form."""

    name = fields.TextField(
        placeholder=_("Family name, First name"),
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-6"),
        # validators=[
        #     validators.Required(),
        # ],
        export_key='full_name',
    )
    affiliation = fields.TextField(
        placeholder=_("Affiliation"),
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-4 col-pad-0"),
        export_key='affiliation',
    )


class SourceInlineForm(WebDepositForm):

    """External source inline form."""

    source = inspire_fields.ExternalSourceField(
        label=_('Identifier'),
        widget=ColumnInput(class_="col-xs-8"),
    )
    import_source = fields.SubmitField(
        label=_('Import data'),
        widget=importdata_button,
    )


class LiteratureForm(WebDepositForm):

    """Literature form fields."""

    identifier = fields.FormField(SourceInlineForm,
                                  widget=ExtendedListWidget(
                                      item_widget=ItemWidget(),
                                      html_tag='div'),
                                  )

    types_of_doc = [("article", _("Article")),
                    ("thesis", _("Thesis")),
                    ("chapter", _("Book Chapter")),
                    ("book", _("Book")),
                    ("proceedings", _("Proceedings")),
                    ]

    # FIXME: change this to radiochoice_buttons widget
    type_of_doc = fields.SelectField(
        label='Type of document',
        choices=types_of_doc,
        default="article",
        #widget=radiochoice_buttons,
        widget_classes='form-control',
        validators=[validators.Required()],
        description='Required.',
    )
    doi = fields.DOIField(
        label=_('DOI'),
        icon='fa fa-barcode fa-fw',
        processors=[missing_doi_warning],
        export_key='doi'
    )

    title = fields.TitleField(
        label=_('Original Title'),
        description='Required.',
        icon='fa fa-book fa-fw',
        widget_classes="form-control",
        validators=[validators.Required()],
        export_key='title',
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
        description='Required.',
        icon='fa fa-user fa-fw',
        min_entries=1,
        widget_classes='',
        export_key='authors',
        validators=[validators.Required()],
    )

    # isto deve ser uma prefilled dropdown
    subject = fields.TextField(
        label=_('Subject'),
        widget_classes="form-control",
        export_key='subject_term',
    )

    abstract = fields.TextAreaField(
        label=_('Abstract'),
        default='',
        icon='fa fa-pencil fa-fw',
        widget_classes="form-control",
        export_key='abstract',
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
        icon='fa fa-user fa-fw',
        min_entries=1,
        export_key='supervisors',
        widget_classes=thesis_class,
    )

    defense_date = fields.Date(
        label=_('Date of Defense'),
        description='Format: YYYY-MM-DD.',
        widget=defensedate_widget,
    )

    degree_type = fields.TextField(
        label=_('Degree type'),
        widget_classes="form-control" + thesis_class,
    )

    university = fields.TextField(
        label=_('University'),
        widget_classes="form-control" + thesis_class,
    )

    # ================
    # Publication Info
    # ================
    journal_title = fields.TextField(
        label=_('Journal Title'),
        widget_classes="form-control"
    )

    isbn = fields.TextField(
        label=_('ISBN'),
        widget_classes="form-control"
    )

    pagination = fields.TextField(
        label=_('Pagination'),
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

    # ====================
    # Fulltext Information
    # ====================
    file_field = fields.FileUploadField(
        label="",
        widget=plupload_widget,
        export_key=False
    )

    url = fields.TextField(
        label=_('External URL'),
        #validators=[validators.URL(), validators.Optional, ],
        placeholder=_("http://www.example.com"),
        widget_classes="form-control",
        export_key='url',
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
    _title = _("Literature suggestion")
    # _subtitle = 'Instructions: (i) Press "Save" to save your upload for '\
    #             'editing later, as many times you like. (ii) Upload or remove'\
    #             ' extra files in the bottom of the form. (iii) When ready, '\
    #             'press "Submit" to finalize your upload. <br><br> If you '\
    #             'already have an <strong>ArXiv</strong> id or a '\
    #             '<strong>DOI</strong>, fill the proper fields and the form '\
    #             'should be automatically completed.'\

    # template = 'deposit/cenas.html'

    # Group fields in categories

    groups = [
        ('Import from existing source',
            ['identifier', ],
            {
                'indication': 'Fill if you have a DOI, ArXiv id or ISBN',
            }),
        ('Document Type',
            ['type_of_doc', ]),
        ('Basic Information',
            ['doi', 'title', 'authors', 'abstract',
             'subject', 'supervisors', 'defense_date', 'degree_type',
             'university']),
        ('Publication Information',
            ['journal_title', 'isbn', 'pagination', 'volume', 'year', 'issue']),
        ('Fulltext Information',
            ['file_field', 'url']),
    ]

    field_sizes = {
        'file_field': 'col-md-12',
        'type_of_doc': 'col-xs-3',
    }


#
# Workflow
#
class literature(SimpleRecordDeposition):

    """Literature deposit submission."""

    workflow = [
        # Pre-fill draft with values passed in from request
        prefill_draft(draft_id='default'),
        # Render form and wait for user to submit
        render_form(draft_id='default'),
        # Create the submission information package by merging form data
        # from all drafts (in this case only one draft exists).
        prepare_sip(),
        # Fills sip with existing ArXiv source
        #harvest_arxiv(),
        # Process metadata to match your JSONAlchemy record model. This will
        # call process_sip_metadata() on your subclass.
        process_sip_metadata(),
        # Reserve a new record id, so that we can provide proper feedback to
        # user before the record has been uploaded.
        create_recid(),
        # Generate MARC based on metadata dictionary.
        finalize_record_sip(is_dump=False),
        # Hold the deposition for admin approval
        hold_for_approval(),
        # Seal the SIP and write MARCXML file and call bibupload on it
        upload_record_sip(),
    ]

    hold_for_upload = False

    name = "Literature"
    name_plural = "Literature depositions"
    group = "Articles & Preprints"
    draft_definitions = {
        'default': LiteratureForm,
    }

    @classmethod
    def process_sip_metadata(cls, deposition, metadata):
        """Map fields to match jsonalchemy configuration."""
        # ========
        # Abstract
        # ========
        if 'abstract' in metadata:
            abstract = metadata['abstract']
            metadata['abstract'] = {}
            metadata['abstract']['abstract'] = fromstring(abstract).text_content()

        # =======
        # Title
        # =======
        title = metadata['title']
        metadata['title'] = {}
        metadata['title']['main'] = title

        # =======
        # Authors
        # =======
        if 'authors' in metadata and metadata['authors']:
            metadata['_first_author'] = metadata['authors'][0]
            metadata['_first_author']['email'] = ''
            if metadata['authors'][1:]:
                metadata['_additional_authors'] = metadata['authors'][1:]
                for k in metadata['_additional_authors']:
                    k['email'] = ''
            del metadata['authors']

        # ===========
        # Supervisors
        # ===========
        if 'supervisors' in metadata and metadata['supervisors']:
            metadata['thesis_supervisor'] = metadata['supervisors'][0]
            metadata['thesis_supervisor']['email'] = ''
            #metadata['_additional_authors'] = metadata['authors'][1:]

        # ==============
        # Thesis related
        # ==============
        if metadata['type_of_doc'] == 'thesis':
            metadata['thesis'] = {}
            metadata['thesis']['date'] = metadata['defense_date']
            metadata['thesis']['university'] = metadata['university']
            metadata['thesis']['type'] = metadata['degree_type']

        # ========
        # Category
        # ========
        metadata['collections'] = {}
        metadata['collections']['primary'] = 'HEP'

        # ================
        # Publication Info
        # ================
        metadata['publication_info'] = {}
        if 'journal_title' in metadata:
            metadata['publication_info']['title'] = metadata['journal_title']
        if 'pagination' in metadata:
            metadata['publication_info']['page_artid'] = metadata['pagination']
        if 'volume' in metadata:
            metadata['publication_info']['journal_volume'] = metadata['volume']
        if 'year' in metadata:
            metadata['publication_info']['year'] = metadata['year']
        if 'issue' in metadata:
            metadata['publication_info']['journal_issue'] = metadata['issue']

        # Delete useless data
        delete_keys = ['supervisors',
                       'defense_date',
                       'degree_type',
                       'university',
                       'journal_title',
                       'pagination',
                       'volume',
                       'year',
                       'issue', ]
        for key in delete_keys:
            if key in metadata:
                del metadata[key]
