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
              {{ record['position'] }}<br/>
            </a>
          </b>
          {% if record['institution'][0]['name']%}
              {% if record['continent'] %}
                ({{ record['institution'][0]['name'] }} - {{ record['continent'] }})
              {% else %}
                ({{ record['institution'][0]['name'] }})
              {% endif %}
            {% endif%}
          {% if record['deadline_date'] %}
            <strong>[Deadline: {{record['deadline_date']}}]</strong>
          {% endif %} 
      </h4>
      <div class="row">
        <div class="col-md-12 record-brief-details">
          {% if record['rank']|is_list %}
            {{ record['rank'][0] }} - 
          {% endif %}
          {% if record['research_area']|is_list %}
            {{ record['research_area']|join(', ') }}
          {% endif %}
        </div>
      </div>
    </div>
  </div>
  </div>
  </div>
</div>
{% endblock %}
