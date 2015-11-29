{#
## This file is part of INSPIRE.
## Copyright (C) 2015 CERN.
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

{% extends "format/record/Default_HTML_brief_base.tpl" %}

{% block record_header %}
<div class="row">
  <div class="col-md-12">
    <div class="panel panel-default custom-panel" >
    <div class="panel-body" >
      <div class="row">
      <div class="col-md-12">
        <h4 class="custom-h">
          <b>
            <a class="title" href="{{ url_for('record.metadata', recid=record['control_number']) }}">{{record['ICN']}}
            </a> 
           {% if record['ICN'] %}
           [Future INSPIRE ID: {{record['ICN']}}]
           {%endif%}
          </b> 
      </h4>
      {% if record['institution'] %}
      <div class="row">
        <div class="col-md-12 record-brief-details" >
         {{ record['institution']}}
        </div>
      </div>
      {% endif %}
      <div class="row">
        <div class="col-md-12 record-brief-details" >
        {% if record['address'][0]['address']|is_list %}
          {{ record['address'][0]['address']|join(', ') }}
        {% else %}
          {{ record['address'][0]['address'] }}
        {% endif %}
        {% if record['address'][0]['country'] %}
          , {{ record['address'][0]['country'] }}
        {% endif %}
        </div>
      </div>
      {% if record['urls'] %}
      <div class="row">
        <div class="col-md-12 record-brief-details" >
          <a href="{{ record['urls'][0] }}">{{ record['urls'][0] }}</a>
        </div>
      </div>
      {% endif %}
      {% if record|link_to_hep_affiliation %}
      <div class="row">
        <div class="col-md-12 record-brief-details" >
          <a href="search?p=affiliation:{{ record['ICN']}}&cc=Hep">{{ record|link_to_hep_affiliation }}</a>
        </div>
      </div>
      {% endif %}
      </div>
    </div>
  </div>
  </div>
  </div>
</div>
{% endblock %}
