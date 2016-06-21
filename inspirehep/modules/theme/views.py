# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Theme blueprint in order for template and static files to be loaded."""

from __future__ import absolute_import, division, print_function

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

from sqlalchemy.orm.exc import NoResultFound

from invenio_mail.tasks import send_email

from flask.ext.menu import current_menu

from inspirehep.modules.records.conference_series import \
    CONFERENCE_CATEGORIES_TO_SERIES

from invenio_search import current_search_client
from invenio_search.api import RecordsSearch
from invenio_pidstore.models import PersistentIdentifier

from inspirehep.utils.citations import Citation
from inspirehep.utils.date import datetime
from inspirehep.utils.search import perform_es_search
from inspirehep.utils.record import get_title
from inspirehep.utils.references import Reference
from inspirehep.utils.template import render_macro_from_template


blueprint = Blueprint('inspirehep_theme', __name__,
                      url_prefix='',
                      template_folder='templates',
                      static_folder='static',
                      )


#
# Collections
#


@blueprint.route('/literature', methods=['GET', ])
@blueprint.route('/collection/literature', methods=['GET', ])
@blueprint.route('/', methods=['GET', 'POST'])
def index():
    """View for literature collection landing page."""
    return render_template(
        'inspirehep_theme/search/collection_literature.html',
        collection='hep')


@blueprint.route('/authors', methods=['GET', ])
@blueprint.route('/collection/authors', methods=['GET', ])
def hepnames():
    """View for authors collection landing page."""
    # collection = {'name': 'hepnames'}
    return render_template('inspirehep_theme/search/collection_authors.html',
                           collection='authors')


@blueprint.route('/conferences', methods=['GET', ])
def conferences():
    """View for conferences collection landing page."""

    today = datetime.today()
    today_str = today.strftime('%Y-%m-%d')

    six_months_str = (today + relativedelta(months=+6)).strftime('%Y-%m-%d')

    upcoming_conferences = perform_es_search(
        'opening_date:{0}->{1}'.format(today_str, six_months_str),
        'records-conferences', 1, 100, {'opening_date': 'asc'})

    results = [hit['_source']
               for hit in upcoming_conferences.to_dict()['hits']['hits']]

    return render_template(
        'inspirehep_theme/search/collection_conferences.html',
        ctx={'conference_subject_areas': CONFERENCE_CATEGORIES_TO_SERIES,
             'results': results},
        collection='conferences')


@blueprint.route('/jobs', methods=['GET', ])
def jobs():
    """View for jobs collection landing page."""
    return redirect(url_for('inspirehep_search.search', cc='jobs'))


@blueprint.route('/institutions', methods=['GET', ])
def institutions():
    """View for institutions collection landing page."""
    institutions_list = perform_es_search('', 'records-institutions', 0, 250)

    results = [hit['_source']
               for hit in institutions_list.to_dict()['hits']['hits']]

    return render_template(
        'inspirehep_theme/search/collection_institutions.html',
        ctx={'results': results}, collection='institutions')


@blueprint.route('/experiments', methods=['GET', ])
def experiments():
    """View for experiments collection landing page."""
    return render_template(
        'inspirehep_theme/search/collection_experiments.html',
        collection='experiments')


@blueprint.route('/journals', methods=['GET', ])
def journals():
    """View for journals collection landing page."""
    return render_template(
        'inspirehep_theme/search/collection_journals.html',
        collection='journals')


@blueprint.route('/data', methods=['GET', ])
def data():
    """View for data collection landing page."""
    return render_template(
        'inspirehep_theme/search/collection_data.html',
        collection='data')


def unauthorized(e):
    """Error handler to show a 401.html page in case of a 401 error."""
    return render_template(current_app.config['THEME_401_TEMPLATE']), 401


def insufficient_permissions(e):
    """Error handler to show a 403.html page in case of a 403 error."""
    return render_template(current_app.config['THEME_403_TEMPLATE']), 403


def page_not_found(e):
    """Error handler to show a 404.html page in case of a 404 error."""
    return render_template(current_app.config['THEME_404_TEMPLATE']), 404


def internal_error(e):
    """Error handler to show a 500.html page in case of a 500 error."""
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
    collection = request.args.get('collection', '')

    pid = PersistentIdentifier.get(collection, recid)

    record = current_search_client.get_source(index='records-hep',
                                              id=pid.object_uuid,
                                              doc_type='hep',
                                              ignore=404)

    return jsonify(
        {
            "data": Reference(record).references()
        }
    )


@blueprint.route('/ajax/citations', methods=['GET'])
def ajax_citations():
    """Handler for datatables citations view"""

    recid = request.args.get('recid', '')
    collection = request.args.get('collection', '')

    pid = PersistentIdentifier.get(collection, recid)

    record = current_search_client.get_source(index='records-hep',
                                              id=pid.object_uuid,
                                              doc_type='hep',
                                              ignore=404)

    return jsonify(
        {
            "data": Citation(record).citations()
        }
    )


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
    search = RecordsSearch(index="records-experiments").query(query)[:100]
    search = search.sort('-earliest_date')

    return search.execute().hits


def get_institution_papers_from_es(recid):
    """
    Get papers where some author is affiliated with institution.

    :param recid: id of the institution.
    :type recid: string
    """
    query = "authors.affiliations.recid:{}".format(recid)
    return perform_es_search(
        query,
        'records-hep',
        sort='-earliest_date',
        size=100,
        fields=[
            'control_number',
            'earliest_date',
            'titles',
            'authors',
            'publication_info',
            'citation_count',
            'collaboration'
        ]
    ).hits


def get_experiment_publications(experiment_name):
    """
    Get paper count for a given experiment.

    :param experiment_name: canonical name of the experiment.
    :type experiment_name: string
    """
    query = {
        "term": {"accelerator_experiments.experiment": experiment_name}
    }
    search = RecordsSearch(index="records-hep").query(query)
    search = search.params(search_type="count")
    return search.execute().hits.total


def get_institution_people_datatables_rows(recid):
    """
    Datatable rows to render people working in an institution.

    :param recid: id of the institution.
    :type recid: string
    """
    query = {
        "query": {
            "term": {
                "authors.affiliations.recid": recid
            }
        },
        "aggs": {
            "authors": {
                "nested": {
                    "path": "authors"
                },
                "aggs": {
                    "affiliated": {
                        "filter": {
                            "term": {"authors.affiliations.recid": recid}
                        },
                        "aggs": {
                            "byrecid": {
                                "terms": {
                                    "field": "authors.recid"
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    records_from_es = current_search_client.search(
        index='records-hep',
        doc_type='hep',
        body=query,
        search_type='count'
    )

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

    results = perform_es_search(
        query, 'records-authors', size=9999, fields=['control_number', 'name']
    )
    recid_map = dict(
        [(int(result.control_number), result.name) for result in results]
    )

    result = []
    author_html_link = "<a href='/authors/{recid}'>{name}</a>"
    for author in papers_per_author:
        row = []
        try:
            row.append(
                author_html_link.format(
                    recid=author['key'],
                    name=recid_map[author['key']].preferred_name
                )
            )
        except:
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
                    name=hit.experiment_names[0].title
                )
            )
        except ValueError:
            row.append(hit.collaboration)
        row.append(get_experiment_publications(
            hit.experiment_names[0].title))
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
                name=get_title(hit.to_dict())
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

    record = current_search_client.get_source(index='records-institutions',
                                              id=pid.object_uuid,
                                              doc_type='institutions',
                                              ignore=404)
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
# Feedback
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
            replytoaddr = current_user.get('email')
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

    current_app.before_first_request_funcs.append(menu_fixup)


#
# Redirect /record/N
#

@blueprint.route('/record/<control_number>')
def record(control_number):
    try:
        pid = PersistentIdentifier.query.filter_by(
            pid_value=control_number).one()
    except NoResultFound:
        abort(404)

    return redirect('/{collection}/{control_number}'.format(
        collection=pid.pid_type, control_number=control_number)), 301
