{#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
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

{% from "format/record/Inspire_Default_HTML_general_macros.tpl" import render_record_authors, record_abstract, record_arxiv, record_cite_modal with context %}

{% from "format/record/Inspire_Default_HTML_brief_macros.tpl" import record_journal_info, render_doi, record_journal_info_and_doi with context %}

{% block record_header %}
<div class="row">
  <div class="col-md-12">
    <div id="panel-default-brief" class="panel panel-default" >
      <div class="panel-body" >
        <div class="row">
          <div class="col-md-9 left-column">
            <div class="row">
              <div class="col-md-1">
                <span id='checkbox-parent'>
                  <input type="checkbox" class="checkbox-results" id="{{ record['control_number'] }}">
                </span>
              </div>
              <div class="col-md-11">
                <h4 class="custom-h">
                  <b>
                    {% if record['titles[0].title']|is_list() %}
                      {% set title = record['titles[0].title[0]'] %}
                    {% else %}
                      {% set title = record['titles[0].title'] %}
                    {% endif %}
                    {% if not title %}
                      {% set title = record['titles.title[0]'] %}
                    {% endif %}
                    <a class="title" href="{{ url_for('record.metadata', recid=record['control_number']) }}">
                      {{ title|capitalize }}
                    </a>
                    {% if title|count_words() > 5 %}
                      <a class="mobile-title" href="{{ url_for('record.metadata', recid=record['control_number']) }}">
                        {{ title|capitalize | words(5) + "..."}}
                      </a>
                    {% else %}
                      <a class="mobile-title" href="{{ url_for('record.metadata', recid=record['control_number']) }}">
                        {{ title|capitalize }}
                      </a>
                    {% endif %}
                </h4>
                {% if record.authors %}
                  <div class="authors">
                    {{ render_record_authors(is_brief=true, show_affiliations=false) }}
                  </div>
                {% endif %}
                <div class="row">
                  {% if record.get('publication_info') and record.get('dois') %}
                    {% if record.get('publication_info') | length == 1 
                    and record.get('dois') | length == 1 %}
                      <div class="col-md-7 ">
                        {{ record_journal_info_and_doi() }}
                      </div>
                    {% else %}
                      <div class="col-md-7 ">
                        {{ record_journal_info() }}
                        <br/>
                        {{ render_doi() }}
                      </div>
                    {% endif %}
                  {% elif record.get('publication_info') %}
                    <div class="col-md-7 ">
                      {{ record_journal_info() }}
                    </div>
                  {% elif record.get('dois') %}
                    <div class="col-md-7 ">
                      {{ render_doi() }}
                    </div>
                  {% endif %}
                  {% if record.get('arxiv_eprints') %}
                    <div class="col-md-5">
                     {{ record_arxiv(is_brief=true) }}
                    </div>
                  {% endif %}
                </div>
                {% if record.get('abstracts') %}
                    {{ record_abstract(is_brief=true) }}
                {% endif %}
              </div>
            </div>
          </div>
          <div class="col-md-3 right-column" >
            {% if record.get('arxiv_eprints') %}
              {% if record.get('arxiv_eprints') | is_list() %}
                {% set eprints = record.get('arxiv_eprints') %}
                {% for eprint in eprints %}
                  <a type="button" class="btn custom-btn btn-warning link-to-pdf no-external-icon" href="http://arxiv.org/pdf/{{ eprint.get('value') | sanitize_arxiv_pdf }}">PDF</a>
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
              {% if record.get('earliest_date') %}
                <i class="glyphicon glyphicon-calendar"></i> {{ record.get('earliest_date').split('-')[0] }}<br/>
              {% endif %}
              {% if  record.get('citation_count') > 0  %}
                <i class="fa fa-quote-left"></i><span><a href="/search?p=refersto:{{ record.get('control_number') }}"> {{ record.get('citation_count') | citation_phrase }} </a></span><br/>
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