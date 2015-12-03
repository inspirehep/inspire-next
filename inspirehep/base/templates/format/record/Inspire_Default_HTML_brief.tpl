{#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
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

{% from "format/record/Inspire_Default_HTML_general_macros.tpl" import render_record_title, render_record_authors, record_abstract, record_arxiv, record_report_numbers, record_cite_modal with context %}

{% from "format/record/Inspire_Default_HTML_brief_macros.tpl" import render_doi with context %}

{% block record_header %}
<div class="row">
  <div class="col-md-12">
    <div id="panel-default-brief" class="panel panel-default" >
    <div class="panel-body" >
      <div class="row">
      <div class="col-md-9"  id="left-column">
        <h4 class="custom-h">
          <span id='checkbox-parent'>
            <input type="checkbox" class="checkbox-results" id="{{ record['control_number'] }}">
          </span>
          <b>
            <a class="title" href="{{ url_for('record.metadata', recid=record['control_number']) }}">
              {{ render_record_title() }}
            </a>
            {% if record['titles[0].title']|count_words() > 5 %}
              <a class="mobile-title" href="{{ url_for('record.metadata', recid=record['control_number']) }}">
              {% if record['titles[0].title']|is_upper() %}
                {{ record['titles[0].title']|capitalize|words(5) + "..."}}
              {% else %}
                {{ record['titles[0].title']|words(5) + "..."}}
              {% endif %}
              </a>
            {% else %}
              <a class="mobile-title" href="{{ url_for('record.metadata', recid=record['control_number']) }}">
              {% if record['titles[0].title']|is_upper() %}
                {{ record['titles[0].title']|capitalize }}
              {% else %}
                {{ record['titles[0].title'] }}
              {% endif %}
              </a>
            {% endif %}
          </b>
      </h4>
      {% if record.authors or record.get('earliest_date') %}
        <div class="authors">
          {% if record.authors %}
            {{ render_record_authors(is_brief=true, show_affiliations=false) }}
          {% endif %}
          {% if record.get('earliest_date') %}
            {{ record.get('earliest_date').split('-')[0] }}
          {% endif %}
        </div>
      {% endif %}
      {% if record.get('publication_info') or record.get('dois') %}
        <div class="row">
          {% if record.get('publication_info') %}
            <div class="col-md-6 ">
              <span class="text-left">{{ record|publication_info|join('<br/>') }}</span>
            </div>
          {% endif %}
          {% if record.get('dois') %}
            <div class="col-md-6 ">
              DOI: {{ render_doi() }}
            </div>
          {% endif %}
        </div>
      {% endif %}
      {% if record['report_numbers'] or record.get('arxiv_eprints') %}
        <div class="row">
          {% if record.get('arxiv_eprints') %}
          <div class="col-md-6">{{ record_arxiv(is_brief=true) }}</div>
          {% endif %}
          {% if record.get('report_numbers') %}
          <div class="col-md-6">
            <span class="text-left">
              {{ record_report_numbers() }}
            </span>
          </div>
          {% endif %}
        </div>
      {% endif %}
      {% if record.get('abstracts') %}
          {{ record_abstract(is_brief=true) }}
      {% endif %} 
        </div>
      <div class="col-md-3" id="right-column" >
        {% if record.get('arxiv_eprints') %}
          {% if record.get('arxiv_eprints') | is_list() %}
            {% set filtered_arxiv = record.get('arxiv_eprints') %}
            {% for i in filtered_arxiv %}
                <a type="button" class="btn  custom-btn blue-btn" id="link-to-pdf"  href="http://arxiv.org/pdf/{{ i.get('value') | sanitize_arxiv_pdf }}"><i class="fa fa-eye"></i> PDF </a>
            {% endfor %}
          {% endif %}
        {% endif %}
        <span class="dropdown">
         <button class="btn btn-default dropdown-toggle dropdown-cite" type="button" id="dropdownMenu{{record['control_number']}}" data-recid="{{record['control_number']}}"  data-toggle="modal" data-target="#citeModal{{record['control_number']}}">
           <i class="fa fa-quote-right"></i> Cite
          </button>
        </span>
        {{ record_cite_modal() }}
        <div class="citations-references">
          {% if record.get('date_updated') %}
            <i class="glyphicon glyphicon-calendar"></i> {{ record.get('date_updated').split('-')[0] }}<br/>
          {% endif %}
          {% if  record.get('_cited_by_count') > 0  %}
            <i class="fa fa-quote-left"></i><span><a href="/record/{{ record.get('control_number') }}#citations"  target="_blank"> Cited {{ record.get('_cited_by_count') }} times</a></span><br/>
          {% else %}
            <i class="fa fa-quote-left"></i><span> Cited 0 times</span><br/>
          {% endif %}
          {% if record.get('references') %}
            <i class="fa fa-link"></i><span><a href="/record/{{ record.get('control_number') }}#references" target="_blank">  {{ (record.get('references', '')) | count }} References</a></span>
          {% else %}
            <i class="fa fa-link"></i><span> 0 References</span>
          {% endif %}
        </div>
      </div>
    </div>
  </div>
</div>
</div>
</div>
{% endblock %}
