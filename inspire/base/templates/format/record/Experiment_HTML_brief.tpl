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
            <a href="{{ url_for('record.metadata', recid=record['control_number']) }}">
              {{ record['experiment_name'][0] }}
            </a>
            {% if record['affiliation'] %}
              ({{record['affiliation'][0]}})
            {% endif %}
          </b> 
      </h4>
      {% if record['breadcrum_title'] %}
      <div class="row">
        <div class="col-md-12 record-brief-details">
        {{ record['breadcrum_title'] }}
        </div>
      </div>
      {% endif %}
      {% if record['urls'] %}
      <div class="row">
        <div class="col-md-12 record-brief-details">
        {{ record['urls'][0]|urlize }}
        </div>
      </div>
      {% endif %}
      <div class="row">
        <div class="col-md-12 record-brief-details">
        <a href="/search?p=experiment:{{ record['experiment_name'][0] }}&cc=HEP">HEP articles associated with {{ record['experiment_name'][0] }}</a>
        </div>
      </div>
      {% if record['collaboration'] %}
      <div class="row">
        <div class="col-md-12 record-brief-details">
        <a href="/search?p=collaboration:{{ record['collaboration'] }}&cc=HEP">{{ record['collaboration'] }}</a>
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

