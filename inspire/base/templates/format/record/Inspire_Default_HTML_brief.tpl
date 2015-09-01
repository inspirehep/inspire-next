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

{% from "format/record/Inspire_Default_HTML_general_macros.tpl" import render_record_authors, record_arxiv with context %}

{% from "format/record/Inspire_Default_HTML_brief_macros.tpl" import record_info, record_journal_info, record_abstract  with context %}

{% block record_header %}
<div class="row">
  <div class="col-md-12">
    <div id="panel-default-brief" class="panel panel-default" >
    <div class="panel-body" >
      <div class="row">
      <div class="col-md-1"><input type="checkbox" class="checkbox-results" id="{{ record['control_number'] }}"></div>
      <div class="col-md-8"  id="left-column">
        <h4 class="custom-h">
          <b>
            {% if record.titles %}
              {% for title in record['titles'] %}
                <a class="title" href="{{ url_for('record.metadata', recid=record['control_number']) }}">
                {{ title['title']|capitalize }}
                </a>
                {% if title['title']|count_words() > 5 %}
                <a class="mobile-title" href="{{ url_for('record.metadata', recid=record['control_number']) }}">
                {{ title['title']|capitalize | words(5) + "..."}}
                </a>
                {% else %}
                 <a class="mobile-title" href="{{ url_for('record.metadata', recid=record['control_number']) }}">
                {{ title['title']|capitalize }}
                {% endif %}
                </a>
              {% endfor %}
            {% endif %}
          </b>
      </h4>
      {{ render_record_authors(10) }}
      <div class="row"><div class="col-md-12"><p></p></div></div>
      <div class="row">
      {% if record.get('publication_info') %}
      <div class="col-md-6 ">
        {{ record_journal_info() }}
      </div>
      {% endif %}
      {% if  record.get('dois') %}
      <div class="col-md-6 ">
        <span class="text-left"><b>DOI:</b></span>{{ record_info() }}
      </div>
      {% endif %}
      </div>
        <div class="row">
          <div class="col-md-6">
           {{ record_arxiv() }}
          </div>
          <div class="col-md-6"></div>
        </div>
        <div class="row"><div class="col-md-12"><p></p></div></div>
        {{ record_abstract() }}
      </div>
      <div class="col-md-3" id="right-column" >
        {% if record.get('arxiv_eprints') %}
          {% if record.get('arxiv_eprints') | is_list() %}
            {% set filtered_arxiv = record.get('arxiv_eprints') %}
            {% for i in filtered_arxiv %}
                <a type="button" class="btn  custom-btn blue-btn" id="link-to-pdf"  href="http://arxiv.org/pdf/{{ i.get('value') }}">PDF </a>
            {% endfor %}
          {% endif %}
        {% endif %}
        <span class="dropdown">
         <button class="btn btn-default dropdown-toggle dropdown-cite" type="button" id="dropdownMenu{{record['control_number']}}" data-recid="{{record['control_number']}}"  data-toggle="modal" data-target="#myModal{{record['control_number']}}">
            Cite
          </button>
        </span>
        <!-- MODAL -->
       <div class="modal fade" id="myModal{{record['control_number']}}" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
        <div class="modal-dialog brief-results-modal">
          <div class="modal-content">
            <div class="modal-header">
              <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
              <h4 class="modal-title" id="myModalLabel">Cite Article</h4>
              <div class="row"><div class="col-md-12"><p></p></div></div>
              <div class="btn-group">
                <button type="button" class="btn btn-primary dropdown-toggle" id="btn-drop" data-toggle="dropdown" aria-expanded="false">
                  Format: <span id="format{{record['control_number']}}"></span> <span class="caret"></span>
                </button>
                <ul class="dropdown-menu" role="menu">
                  <li><a class="pointer bibtex" id="bibtex{{record['control_number']}}" data-recid="{{record['control_number']}}">BibTex</a></li>
                  <li><a class="pointer latex_eu" id="latex_eu{{record['control_number']}}" data-recid="{{record['control_number']}}">LaTex(EU)</a></li>
                  <li><a class="pointer latex_us" id="latex_us{{record['control_number']}}" data-recid="{{record['control_number']}}">LaTex(US)</a></li>
                </ul>
              </div>
              <a type="button" id="download{{record['control_number']}}" class="btn btn-primary">Download</a>
            </div>
            <div class="modal-body">
              <div class="row">
                <div class="col-md-12">
                  <div class="editable" contenteditable="true" onclick="document.execCommand('selectAll',false,null)"><pre id="text{{record['control_number']}}"></pre></div>
                </div>
              </div>
            </div>
            <div class="modal-footer">
            </div>
            </div>
          </div>
        </div>
          <!-- END MODAL -->
        <div class="citations-references">
          {% if record.get('date_updated') %}
            <i class="glyphicon glyphicon-calendar"></i> {{ record.get('date_updated').split('-')[0] }}<br/>
          {% endif %}
          {% if  record.get('_cited_by_count') > 0  %}
            <i class="fa fa-quote-left"></i><span><a href="/record/{{ record.get('control_number') }}/citations"  target="_blank"> Cited {{ record.get('_cited_by_count') }} times</a></span><br/>
          {% else %}
            <i class="fa fa-quote-left"></i><span> Cited 0 times</span><br/>
          {% endif %}
          {% if record.get('references') %}
            <i class="fa fa-link"></i><span><a href="/record/{{ record.get('control_number') }}/references" target="_blank">  {{ (record.get('references', '')) | count }} References</a></span>
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
