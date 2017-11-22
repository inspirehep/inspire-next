{#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015, 2016 CERN.
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
{%- extends "inspirehep_theme/page.html" -%}

{% from "inspirehep_theme/format/record/Inspire_HTML_detailed_macros.tpl" import record_buttons, record_collections, record_publication_info, record_doi, record_links, detailed_record_abstract, record_keywords, record_references, record_citations, record_plots, record_doi, record_experiment, impactgraph with context %}

{% from "inspirehep_theme/format/record/Inspire_Default_HTML_general_macros.tpl" import mathjax, render_record_title, render_record_authors, record_arxiv, record_report_numbers with context %}

{% set title=record.title %}

{% block body %}
<ul class="breadcrumb detailed-record-breadcrumb">
<li>
  <span class="fa fa-chevron-left"></span>
  {{ request.headers.get('referer', '')|back_to_search_link("literature") }}
</li>
</ul>
<div id="record_content">
  <div class="record-detailed record-detailed-literature">
    <div class="record-header record-header-literature">
      <div class="row">
        <div class="col-md-12">
          <h1 class="record-detailed-title">{{ render_record_title(record) }}</h1>
          <div id="record-authors">
            {{ render_record_authors(record, is_brief=false, number_of_displayed_authors=25) }}
            <span id="record-date">- {{ record.get('earliest_date')|format_date }}</span>
          </div>
          <div id="record-journal">
            {% if record|publication_info %}
            {{ record_publication_info(record) }}
          {% endif %}
          </div>
          {% if record.get('report_numbers') %}
          <div id="record-report-numbers">{{ record_report_numbers(record) }}</div>
          {% endif %}
          {% if record.get('number_of_pages') %}
            <div> Number of pages: {{ record.number_of_pages }} </div>
          {% endif %}
          {% if record.get('dois') or record.get('arxiv_eprints') %}
            <div id="doi-eprint-experiment">
              {% if record.get('dois') %}
                {{ record_doi(record) }}
              {% endif %}
              {% if record.get('arxiv_eprints') %}
                {{ record_arxiv(record) }}
              {% endif %}
            </div>
          {% endif %}
          {% if record.get('accelerator_experiments') %}
            <div> Experiment: {{ record_experiment(record) }} </div>
          {% endif %}
        {% if record.urls or record.external_system_identifiers %}
          <div id="external_links">{{ record_links(record) }}</div>
        {% endif %}
        </div>
        <div class="col-md-12 detailed-action-bar" id="cite-pdf-buttons">
          <div class="btn-group">{{ record_buttons(record) }}</div>
        </div>
        {% if record.admin_tools %}
        <div class="col-md-12" id="admin-tools">
          {% for tool in record.admin_tools %}
            {% if tool == 'editor' %}
              <a href="/editor/literature/{{record.control_number}}"><i class="fa fa-pencil" aria-hidden="true"></i> Edit</a>
            {% endif %}
          {% endfor %}
        </div>
        {% endif %}
      </div>
    </div>

    <div class="row">
      <div class="col-md-8">
        <div class="panel">
          <div class="panel-heading">Abstract</div>
          <div class="panel-body">
            <div class="row">
              <div class="col-md-12">{{ detailed_record_abstract(record) }}</div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="panel">
          <div class="panel-heading">Keywords</div>
          <div class="panel-body">{{ record_keywords(record) }}</div>
        </div>
      </div>
    </div>
    {% set plot_count = record | count_plots %}
    {% if plot_count %}
      <div class="row">
        <div class="col-md-12">
          <div class="panel">
            <div class="panel-heading">Plots ({{plot_count}})</div>
            <div class="panel-body">{{ record_plots(record) }}</div>
          </div>
        </div>
      </div>
    {% endif %}
    <div class="row">
      <div class="col-md-12">{{ record_references(record) }}</div>
    </div>
    <div class="row">
      <div class="col-md-12">{{ record_citations(record) }}</div>
    </div>
    <div class="row">
      <div class="col-md-12">{{ impactgraph() }}</div>
    </div>
  </div>
</div>
{% endblock body %}


{% block javascript %}
{{ super() }}
{%- assets "inspirehep_detailed_js" %}
<script src="{{ ASSET_URL }}"></script>
{%- endassets %}
{% endblock javascript %}

{% block additional_javascript %}
  {{ mathjax() | safe }}
  <script type="text/javascript">
    require([
      "jquery",
      ], function ($) {
        $(document).ready(function () {
          MathJax.Hub.Queue(['Typeset', MathJax.Hub]);
        })
      }
    );
  </script>
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
          'endpoint': "literature",
          {% if record['series'] %}
            'seriesname' : "{{ record['series'][0] }}"
          {% endif %}
        });
      });
  </script>
<script>
    require(
      [
        "impact-graphs",
      ],

      function(
        ImpactGraph
      ) {
          $(".impact-graph-container").append('<div id="impact_graph_chart_' + '{{record["control_number"]}}' + '"></div>');
          ImpactGraph.draw_impact_graph('/api/literature/{{record["control_number"]}}#impact_graph_chart_{{record["control_number"]}}',
            '#impact_graph_chart_' + '{{record["control_number"]}}',
            {
              width: 940,
              height: 280,
              'content-type': 'application/x-impact.graph+json',
              y_scale: 'linear',
              show_axes: true,
            }
          );
        }
    );
  </script>
  {% include "inspirehep_theme/typeahead.html" %}
{% endblock additional_javascript %}
