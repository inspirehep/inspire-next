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

"""Theme views."""

from __future__ import absolute_import, division, print_function

import sys
from datetime import date
from functools import wraps

import six
from dateutil.relativedelta import relativedelta
from flask import (
    Blueprint,
    abort,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user
from flask_menu import current_menu
from sqlalchemy.orm.exc import NoResultFound

from invenio_mail.tasks import send_email
from invenio_pidstore.models import PersistentIdentifier

from inspirehep.modules.pidstore.utils import (
    get_endpoint_from_pid_type,
    get_pid_type_from_endpoint,
)
from inspirehep.modules.records.conference_series import (
    CONFERENCE_CATEGORIES_TO_SERIES,
)
from inspirehep.modules.search import (
    AuthorsSearch,
    ConferencesSearch,
    DataSearch,
    ExperimentsSearch,
    InstitutionsSearch,
    JournalsSearch,
    LiteratureSearch
)
from inspirehep.utils.citations import get_and_format_citations
from inspirehep.utils.conferences import (
    render_conferences_contributions,
    render_conferences_in_the_same_series,
)
from inspirehep.utils.experiments import (
    render_experiment_contributions,
    render_experiment_people,
)
from inspirehep.utils.record import get_title
from inspirehep.utils.references import get_and_format_references
from inspirehep.utils.template import render_macro_from_template


blueprint = Blueprint(
    'inspirehep_theme',
    __name__,
    url_prefix='',
    template_folder='templates',
    static_folder='static',
)


#
# Collections
#

@blueprint.route('/literature', methods=['GET', ])
@blueprint.route('/collection/literature', methods=['GET', ])
@blueprint.route('/', methods=['GET', ])
def index():
    """View for literature collection landing page."""
    if current_app.config['INSPIRE_FULL_THEME']:
        number_of_records = LiteratureSearch().count()

        return render_template(
            'inspirehep_theme/search/collection_literature.html',
            collection='hep',
            number_of_records=number_of_records,
        )
    else:
        return render_template('inspirehep_theme/inspire_labs_cover.html')


@blueprint.route('/authors', methods=['GET', ])
@blueprint.route('/collection/authors', methods=['GET', ])
def hepnames():
    """View for authors collection landing page."""
    number_of_records = AuthorsSearch().count()

    return render_template(
        'inspirehep_theme/search/collection_authors.html',
        collection='authors',
        number_of_records=number_of_records,
    )


@blueprint.route('/conferences', methods=['GET', ])
def conferences():
    """View for conferences collection landing page."""
    number_of_records = ConferencesSearch().count()
    upcoming_conferences = _get_upcoming_conferences()

    return render_template(
        'inspirehep_theme/search/collection_conferences.html',
        collection='conferences',
        conferences_subject_areas=CONFERENCE_CATEGORIES_TO_SERIES,
        number_of_records=number_of_records,
        result=upcoming_conferences,
    )


@blueprint.route('/jobs', methods=['GET', ])
def jobs():
    """View for jobs collection landing page."""
    return redirect(url_for('inspirehep_search.search', cc='jobs'))


@blueprint.route('/institutions', methods=['GET', ])
def institutions():
    """View for institutions collection landing page."""
    number_of_records = InstitutionsSearch().count()
    some_institutions = _get_some_institutions()

    return render_template(
        'inspirehep_theme/search/collection_institutions.html',
        collection='institutions',
        number_of_records=number_of_records,
        result=some_institutions,
    )


@blueprint.route('/experiments', methods=['GET', ])
def experiments():
    """View for experiments collection landing page."""
    number_of_records = ExperimentsSearch().count()

    return render_template(
        'inspirehep_theme/search/collection_experiments.html',
        collection='experiments',
        number_of_records=number_of_records,
    )


@blueprint.route('/journals', methods=['GET', ])
def journals():
    """View for journals collection landing page."""
    number_of_records = JournalsSearch().count()

    return render_template(
        'inspirehep_theme/search/collection_journals.html',
        collection='journals',
        number_of_records=number_of_records,
    )


@blueprint.route('/data', methods=['GET', ])
def data():
    """View for data collection landing page."""
    number_of_records = DataSearch().count()

    return render_template(
        'inspirehep_theme/search/collection_data.html',
        collection='data',
        number_of_records=number_of_records,
    )


#
# Error handlers
#

def api_friendly_error_handler(f):
    @wraps(f)
    def wrapper(error, *args, **kwargs):
        if current_app.config.get('RESTFUL_API'):
            try:
                return jsonify(code=error.code, message=error.name), error.code
            except Exception:
                six.reraise(*sys.exc_info())
        return f(error, *args, **kwargs)

    return wrapper


@api_friendly_error_handler
def unauthorized(error):
    return render_template(current_app.config['THEME_401_TEMPLATE']), 401


@api_friendly_error_handler
def insufficient_permissions(error):
    return render_template(current_app.config['THEME_403_TEMPLATE']), 403


@api_friendly_error_handler
def page_not_found(error):
    return render_template(current_app.config['THEME_404_TEMPLATE']), 404


@api_friendly_error_handler
def internal_error(error):
    return render_template(current_app.config['THEME_500_TEMPLATE']), 500


#
# Ping
#

@blueprint.route('/ping')
def ping():
    return 'OK'


#
# Handlers for AJAX requests regarding references and citations
#

@blueprint.route('/ajax/references', methods=['GET'])
def ajax_references():
    """Handler for datatables references view"""
    recid = request.args.get('recid', '')
    endpoint = request.args.get('endpoint', '')

    pid_type = get_pid_type_from_endpoint(endpoint)
    pid = PersistentIdentifier.get(pid_type, recid)

    record = LiteratureSearch().get_source(pid.object_uuid)

    return jsonify({'data': get_and_format_references(record)})


@blueprint.route('/ajax/citations', methods=['GET'])
def ajax_citations():
    """Handler for datatables citations view"""
    recid = request.args.get('recid', '')
    endpoint = request.args.get('endpoint', '')

    pid_type = get_pid_type_from_endpoint(endpoint)
    pid = PersistentIdentifier.get(pid_type, recid)

    record = LiteratureSearch().get_source(pid.object_uuid)

    return jsonify({'data': get_and_format_citations(record)})


#
# Handlers for AJAX requests regarding institution detailed view
#

def get_institution_experiments_from_es(icn):
    """
    Get experiments from a given institution.

    To avoid killing ElasticSearch the number of experiments is limited.

    :param icn: Institution canonical name.
    :type icn: string
    """
    query = {
        "term": {"affiliation": icn}
    }
    search = ExperimentsSearch().query(query)[:100]
    search = search.sort('-earliest_date')

    return search.execute().hits


def get_institution_papers_from_es(recid):
    """
    Get papers where some author is affiliated with institution.

    :param recid: id of the institution.
    :type recid: string
    """
    return LiteratureSearch().query_from_iq(
        'authors.affiliations.recid:{}'.format(recid)
    ).sort(
        '-earliest_date'
    ).params(
        size=100,
        _source=[
            'control_number',
            'earliest_date',
            'titles',
            'authors',
            'publication_info',
            'citation_count',
            'collaboration'
        ]
    ).execute().hits


def get_experiment_publications(experiment_name):
    """
    Get paper count for a given experiment.

    :param experiment_name: canonical name of the experiment.
    :type experiment_name: string
    """
    query = {
        "term": {"accelerator_experiments.experiment": experiment_name}
    }
    search = LiteratureSearch().query(query)
    search = search.params(search_type="count")
    return search.execute().hits.total


def get_institution_people_datatables_rows(recid):
    """
    Datatable rows to render people working in an institution.

    :param recid: id of the institution.
    :type recid: string
    """
    query = LiteratureSearch().query(
        "term",
        authors__affiliations__recid=recid
    )
    query = query.params(search_type="count")

    query.aggs.bucket("authors", "nested", path="authors")\
        .bucket("affiliated", "filter", term={
            "authors.affiliations.recid": recid
        })\
        .bucket('byrecid', 'terms', field='authors.recid')

    records_from_es = query.execute().to_dict()

    # Extract all the record ids from the aggregation
    papers_per_author = records_from_es[
        'aggregations'
    ]['authors']['affiliated']['byrecid']['buckets']
    recids = [int(paper['key']) for paper in papers_per_author]

    # Generate query to retrieve records from author index
    query = ""
    for i, recid in enumerate(recids):
        query += "recid:{}".format(recid)
        if i != len(recids) - 1:
            query += " OR "

    results = AuthorsSearch().query_from_iq(
        query
    ).params(
        size=9999,
        _source=['control_number', 'name']
    ).execute()

    recid_map = dict(
        [(result.control_number, result.name) for result in results]
    )

    result = []
    author_html_link = u"<a href='/authors/{recid}'>{name}</a>"
    for author in papers_per_author:
        row = []
        try:
            row.append(
                author_html_link.format(
                    recid=author['key'],
                    name=recid_map[author['key']].preferred_name
                )
            )
        except Exception:
            # No preferred name, use value
            row.append(
                author_html_link.format(
                    recid=author['key'],
                    name=recid_map[author['key']].value
                )
            )
        row.append(author['doc_count'])
        result.append(row)

    return result


def get_institution_experiments_datatables_rows(hits):
    """Row used by datatables to render institution experiments."""
    result = []

    name_html = "<a href='/experiments/{id}'>{name}</a>"

    for hit in hits:
        row = []
        try:
            row.append(
                name_html.format(
                    id=hit.control_number,
                    name=hit.legacy_name,
                )
            )
        except ValueError:
            row.append(hit.collaboration)
        row.append(get_experiment_publications(hit.legacy_name))
        result.append(row)
    return result


def get_institution_papers_datatables_rows(hits):
    """Row used by datatables to render institution papers."""
    result = []

    title_html = "<a href='/literature/{id}'>{name}</a>"

    for hit in hits:
        row = []
        row.append(
            title_html.format(
                id=hit.control_number,
                name=get_title(hit.to_dict()).encode('utf8')
            )
        )
        ctx = {
            'record': hit.to_dict(),
            'is_brief': 'true',
            'number_of_displayed_authors': 1,
            'show_affiliations': 'false',
            'collaboration_only': 'true'
        }
        row.append(render_macro_from_template(
            name="render_record_authors",
            template="inspirehep_theme/format/record/Inspire_Default_HTML_general_macros.tpl",
            ctx=ctx
        )
        )
        try:
            row.append(hit.publication_info[0].journal_title)
        except AttributeError:
            row.append('')

        try:
            row.append(hit.citation_count)
        except AttributeError:
            row.append(0)

        row.append(hit.earliest_date.split('-')[0])

        result.append(row)

    return result


@blueprint.route('/ajax/institutions/people', methods=['GET'])
def ajax_institutions_people():
    """Datatable handler to get people working in an institution."""
    institution_recid = request.args.get('recid', '')

    return jsonify(
        {
            "data": get_institution_people_datatables_rows(institution_recid)
        }
    )


@blueprint.route('/ajax/institutions/experiments', methods=['GET'])
def ajax_institutions_experiments():
    """Datatable handler to get experiments in an institution."""
    recid = request.args.get('recid', '')

    pid = PersistentIdentifier.get('institutions', recid)

    record = InstitutionsSearch().get_source(pid.object_uuid)
    try:
        icn = record.get('ICN', [])[0]
    except KeyError:
        icn = ''

    hits = get_institution_experiments_from_es(icn)
    return jsonify(
        {
            "data": get_institution_experiments_datatables_rows(hits),
            "total": hits.total
        }
    )


@blueprint.route('/ajax/institutions/papers', methods=['GET'])
def ajax_institutions_papers():
    """Datatable handler to get papers from an institution."""
    recid = request.args.get('recid', '')

    hits = get_institution_papers_from_es(recid)
    return jsonify(
        {
            "data": get_institution_papers_datatables_rows(hits),
            "total": hits.total
        }
    )


#
# Feedback handler
#

@blueprint.route('/postfeedback', methods=['POST', ])
def postfeedback():
    """Handler to create a ticket from user feedback."""
    feedback = request.form.get('feedback')
    if feedback == '':
        return jsonify(success=False), 400

    replytoaddr = request.form.get('replytoaddr', None)
    if replytoaddr is None:
        if current_user.is_anonymous:
            return jsonify(success=False), 403
        else:
            replytoaddr = current_user.email
            if replytoaddr == '':
                return jsonify(success=False), 403

    content = 'Feedback:\n{feedback}'.format(feedback=feedback)
    message = {
        'sender': current_app.config['CFG_SITE_SUPPORT_EMAIL'],
        'recipients': [current_app.config['INSPIRELABS_FEEDBACK_EMAIL']],
        'subject': 'INSPIRE Labs Feedback',
        'body': content,
        'reply_to': replytoaddr
    }

    sending = send_email.delay(message)

    if sending.failed():
        return jsonify(success=False), 500
    else:
        return jsonify(success=True)


#
# Menu fixup
#

@blueprint.before_app_first_request
def register_menu_items():
    """Hack to remove children of Settings menu"""

    def menu_fixup():
        current_menu.submenu("settings.change_password").hide()
        current_menu.submenu("settings.groups").hide()
        current_menu.submenu("settings.workflows").hide()
        current_menu.submenu("settings.applications").hide()
        current_menu.submenu("settings.oauthclient").hide()
        current_menu.submenu("settings.security").hide()

    current_app.before_first_request_funcs.append(menu_fixup)


#
# Legacy redirects
#

@blueprint.route('/record/<control_number>')
def record(control_number):
    try:
        pid = PersistentIdentifier.query.filter_by(
            pid_value=control_number).one()
    except NoResultFound:
        abort(404)

    return redirect('/{endpoint}/{control_number}'.format(
        endpoint=get_endpoint_from_pid_type(pid.pid_type),
        control_number=control_number)), 301


@blueprint.route('/author/new')
def author_new():
    bai = request.values.get('bai', None, type=str)
    return redirect(url_for('inspirehep_authors.new', bai=bai)), 301


@blueprint.route('/author/update')
def author_update():
    recid = request.values.get('recid', None, type=str)
    if recid:
        return redirect(
            url_for('inspirehep_authors.update', recid=recid)
        ), 301
    else:
        return redirect(url_for('inspirehep_authors.new')), 301


@blueprint.route('/submit/literature/create')
def literature_new():
    return redirect(url_for('inspirehep_literature_suggest.create')), 301


#
# Handlers for AJAX requests regarding conferences detailed views
#

@blueprint.route('/ajax/conferences/series', methods=['GET'])
def ajax_other_conferences():
    """Handler for other conferences in the series"""
    recid = request.args.get('recid', '')
    seriesname = request.args.get('seriesname', '')

    html, total = render_conferences_in_the_same_series(recid, seriesname)
    return jsonify(
        {
            "data": html,
            "total": total
        }
    )


@blueprint.route('/ajax/conferences/contributions', methods=['GET'])
def ajax_conference_contributions():
    """Handler for other conference contributions"""
    cnum = request.args.get('cnum', '')

    html, total = render_conferences_contributions(cnum)

    return jsonify(
        {
            "data": html,
            "total": total
        }
    )


@blueprint.route('/ajax/experiments/contributions', methods=['GET'])
def ajax_experiment_contributions():
    """Handler for experiment contributions"""
    experiment_name = request.args.get('experiment_name', '')

    html, total = render_experiment_contributions(experiment_name)

    return jsonify(
        {
            "data": html,
            "total": total
        }
    )


@blueprint.route('/ajax/experiments/people', methods=['GET'])
def ajax_experiments_people():
    """Datatable handler to get people working in an experiment."""
    experiment_name = request.args.get('experiment_name', '')

    html, total = render_experiment_people(experiment_name)

    return jsonify(
        {
            "data": html,
            "total": total
        }
    )


#
# Redirect on login with ORCID
#

@blueprint.route('/account/settings/linkedaccounts/', methods=['GET'])
def linkedaccounts():
    """Redirect to the homepage when logging in with ORCID."""
    return redirect('/')


#
# Helpers
#

def _get_some_institutions():
    some_institutions = InstitutionsSearch().query_from_iq(
        ''
    )[:250].execute()

    return [hit['_source'] for hit in some_institutions.to_dict()['hits']['hits']]


def _get_upcoming_conferences():
    today = date.today()
    in_six_months = today + relativedelta(months=+6)

    upcoming_conferences = ConferencesSearch().query_from_iq(
        'opening_date:{0}->{1}'.format(str(today), str(in_six_months))
    ).sort(
        {'opening_date': 'asc'}
    )[1:100].execute()

    return [hit['_source'] for hit in upcoming_conferences.to_dict()['hits']['hits']]
