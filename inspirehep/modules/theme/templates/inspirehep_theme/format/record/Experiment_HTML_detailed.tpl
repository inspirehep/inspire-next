{#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#}

{% extends "inspirehep_theme/format/record/Inspire_Default_HTML_detailed.tpl" %}

{% set title=record.title %}

{% block body %}
<ul class="breadcrumb detailed-record-breadcrumb">
<li>
  <span class="fa fa-chevron-left"></span>
  {{ request.headers.get('referer', '')|back_to_search_link("experiments") }}
</li>
</ul>
<div id="record_content">
  <div class="record-detailed record-detailed-experiments">
    <div class="panel">
      <div class="panel-heading">
        <h1 class="record-detailed-title">
          {{ record['legacy_name'] }}
            {% if record['affiliations'] %}
              ({{ record['affiliations'][0]['name'] }})
            {% endif %}
        </h1>
        {% if record['titles'] %}
          <h2 class="record-detailed-subtitle record-detailed-subtitle-experiments">{{ record['titles'][0].title }}</h2>
        {% endif %}
        {% if record['long_name'] %}
          <h2 class="record-detailed-subtitle">{{ record['long_name'] }}</h2>
        {% endif %}
      </div>
      <div class="panel-body">
        <div class="row">
          <div class="col-md-12">

            {% if record['urls'] %}
            <div class="detailed-record-field">
              <label>Link to the experiment's website:</label>
              {% for url in record['urls'] %}
                <a href="{{ url['value'] }}">{{ url['value'] }}</a><br>
              {% endfor %}
            </div>
            {% endif %}

            {% if record['date_started'] %}
              <div class="detailed-record-field">
                <label>Dates:</label>
                {{ record|experiment_date }}
                <br></div>
            {% endif %}

            {% if record['spokespersons'] %}
              <div class="detailed-record-field">
                <label>Spokesperson:</label>
                {% for spokesperson in record['spokespersons'] %}
                {{ spokesperson.name }}{% if not loop.last %}; {% endif %}
              {% endfor %}
              </div>
              {% endif %}

            {% if record['contact_details'] %}
              <div class="detailed-record-field">
                <label>Contact email:</label>
                {% for contact in record['contact_details'] %}
                  {% if contact.email %}
                    {{ contact.email | email_link }}{% if not loop.last %}; {% endif %}
                  {% endif %}
                {% endfor %}
              </div>
            {% endif %}
            {% if record['related_experiments'] %}
            <div class="detailed-record-field">
              <label>Related Experiments:</label>
              {{ record|experiment_link|join(', ') }}
            </div>
            {% endif %}
            {% if record['collaboration'] %}
            <hr>
            <div>
              Part of the
              <strong><a href="/search?p=collaboration:{{ record['collaboration'] }}&cc=Hep">{{ record['collaboration']['value'] }}</a></strong> collaboration - <a href="https://inspirehep.net/search?ln=en&ln=en&p=693__e%3A{{record['legacy_name']}}&of=hcs">See Citesummary</a>
            </div>
            {% endif %}
          </div>
        </div>
      </div>
      {% if record.admin_tools %}
          <div class="col-md-12" id="admin-tools">
            {% for tool in record.admin_tools %}
              {% if tool == 'editor' %}
                <a href="/editor/experiments/{{record.control_number}}"><i class="fa fa-pencil" aria-hidden="true"></i> Edit</a>
              {% endif %}
            {% endfor %}
          </div>
          <br>
        {% endif %}

    </div>
    <div class="row">
      <div class="col-md-12">
        <div class="panel">
          <div class="panel-heading">Description</div>
          <div class="panel-body">
            {% if record['description'] %}
            <div class="detailed-record-field">{{ record['description'] }}</div>
            {% endif %}
          </div>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col-md-12">
        <div class="panel panel-datatables" id="record-experiment-papers">
          <div class="panel-heading">Papers associated with {{ record['legacy_name'] }}</div>
          <div class="panel-body">
            <div class="datatables-loading">
              <i class="fa fa-spinner fa-spin fa-lg" ></i>
              <br>Loading papers...
            </div>
            <div class="datatables-wrapper">
              <table id="record-experiment-papers-table" class="table table-striped table-bordered table-with-ellipsis" cellspacing="0" width="100%">
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Authors</th>
                    <th>Journal</th>
                    <th># Citations</th>
                  </tr>
                </thead>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col-md-12">
        <div class="panel panel-datatables" id="record-experiment-people">
          <div class="panel-heading">Collaboration members</div>
          <div class="panel-body">
            <div class="datatables-loading"> <i class="fa fa-spinner fa-spin fa-lg" ></i>
              <br>Loading authors...
            </div>
            <div class="datatables-wrapper">
              <table id="record-experiment-people-table" class="table table-striped table-bordered" cellspacing="0" width="100%">
                <thead>
                  <tr>
                    <th>Name</th>
                  </tr>
                </thead>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
{% endblock %}


{% block additional_javascript %}
  <script type="text/javascript">
  require(
    [
      "js/datatables",
    ],
    function(
      DataTables
    ) {
      DataTables.attachTo(document, {
        'recid': "{{ record.control_number }}",
        'experiment_name': "{{record['legacy_name']}}",
      });
    });
  </script>
{% endblock additional_javascript %}
