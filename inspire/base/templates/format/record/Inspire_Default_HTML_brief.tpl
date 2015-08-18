{#
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
#}
 

{% from "format/record/Inspire_Default_HTML_general_macros.tpl" import render_record_authors, record_arxiv with context %}

{% from "format/record/Inspire_Default_HTML_brief_macros.tpl" import record_info, record_journal_info, record_abstract  with context %}

{% block record_header %}
<div class="row">
  <div class="col-md-12">
    <div class="panel panel-default custom-panel" >
    <div class="panel-body" >
      <div class="row">
      <div class="col-md-9"  id="left-column">
        <h4 class="custom-h">
          <b>
            {% if record['title']|is_list %}
              {% for title in record['title'] %}          
                <a class="title" href="{{ url_for('record.metadata', recid=record['recid']) }}">
                {{ title['title']|capitalize }}
                </a>
                {% if title['title']|count_words() > 5 %}
                <a class="mobile-title" href="{{ url_for('record.metadata', recid=record['recid']) }}">
                {{ title['title']|capitalize | words(5) + "..."}}
                </a>
                {% else %}
                 <a class="mobile-title" href="{{ url_for('record.metadata', recid=record['recid']) }}">
                {{ title['title']|capitalize }}
                {% endif %}
                </a> 
              {% endfor %}
            {% else %}
              <a class="title" href="{{ url_for('record.metadata', recid=record['recid']) }}">
              {{ record['title']['title']|capitalize }}
              </a>
              {% if record['title']['title']|count_words() > 5 %}
              <a class="mobile-title" href="{{ url_for('record.metadata', recid=record['recid']) }}">
              {{ record['title']['title']|capitalize | words(5) + "..."}}
              </a>
              {% else %}
               <a class="mobile-title" href="{{ url_for('record.metadata', recid=record['recid']) }}">
              {{ record['title']['title']|capitalize }}
              {% endif %}
              </a> 
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
      {% if  record.get('doi') %}
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
        {% if record.get('report_number') %}
        {% if record.get('report_number') | is_list() %}
        {% set filtered_arxiv = record.get('report_number')| remove_duplicates_from_dict() %}
        {% for i in filtered_arxiv %}
        {% if i.get('source') == 'arXiv' %}
          <a type="button" class="btn  custom-btn blue-btn" id="link-to-pdf"  href="http://arxiv.org/pdf/{{ i.get('primary') }}">PDF </a>
        {% endif %}
        {% endfor %}
        {% endif %}
        {% endif %}
        <span class="dropdown">
         <button class="btn btn-default dropdown-toggle dropdown-cite" type="button" id="dropdownMenu{{record['recid']}}" data-recid="{{record['recid']}}"  data-toggle="modal" data-target="#myModal{{record['recid']}}">
            Cite
          </button>
        </span>
        <!-- MODAL -->
       <div class="modal fade" id="myModal{{record['recid']}}" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
              <h4 class="modal-title" id="myModalLabel">Export Article</h4>
              <div class="btn-group">
              <button type="button" class="btn btn-primary dropdown-toggle" id="btn-drop" data-toggle="dropdown" aria-expanded="false">
                Format: BibTex <span class="caret"></span>
              </button>
              <ul class="dropdown-menu" role="menu">
                <li><a class="pointer bibtex" id="bibtex{{record['recid']}}" data-recid="{{record['recid']}}">BibTex</a></li>
                <li><a class="pointer latex_eu" id="latex_eu{{record['recid']}}" data-recid="{{record['recid']}}">Latex(EU)</a></li>
              </ul>
            </div>
                <button type="button" class="btn  btn-primary">Download</button>
            </div>
            <div class="modal-body">
              <div class="row">
                <div class="col-md-12">
                  <div class="editable" contenteditable="true" onclick="document.execCommand('selectAll',false,null)"><pre id="text{{record['recid']}}"></pre></div>
                </div>
              </div> 
            </div>
            <div class="modal-footer">
            </div>
            </div>
          </div>
        </div>
          <!-- END MODAL -->
        <div class="row"><div class="col-md-12"><p></p></div></div>
        <div class="row"><div class="col-md-12"><p></p></div></div>
        {% if record.get('date_updated') %}
        <i class="glyphicon glyphicon-calendar"></i> {{ record.get('date_updated').split('-')[0] }}<br/>
        {% endif %}               
        {% if  record.get('_cited_by_count') > 0  %}
        <i class="fa fa-quote-left"></i><span><a href="/record/{{ record.get('_id') }}/citations"  target="_blank"> Cited {{ record.get('_cited_by_count') }} times</a></span><br/>
        {% else %}
        <i class="fa fa-quote-left"></i><span> Cited {{ record.get('_cited_by_count') }} times</span><br/>
        {% endif %}
        {% if record.get('reference') %}
        <i class="fa fa-link"></i><span><a href="/record/{{ record.get('_id') }}/references" target="_blank">  {{ (record.get('reference', '')) | count }} References</a></span>
        {% else %}
        <i class="fa fa-link"></i><span> References ({{ (record.get('reference', '')) | count }})</span>
        {% endif %}
      </div>
    </div>
  </div>
</div>
</div>
</div>
{% endblock %}


