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

{% extends "inspirehep_theme/format/record/Default_HTML_brief_base.tpl" %}

{% block record_header %}
<div class="row">
  <div class="col-md-12">
    <div class="panel panel-default custom-panel" >
    <div class="panel-body" >
      <div class="row">
      <div class="col-md-12">
        <h4 class="custom-h">
            <a href="{{ url_for('record.metadata', recid=record['control_number']) }}">
              {{ record.get('name.preferred_name', '') }} 
              {% if record['native_name']%}
                ({{ record['native_name']}})
              {% endif %}
            </a>
            {% set institution = [] %}
            {% if record['positions'] %}
              {% for rec in record['positions'] %}
                {% if rec.get('institution', {}).get('name') %}
                  {% do institution.append(rec.get('institution', {}).get('name')) %}
                {% endif %}
              {% endfor %}
              {% if institution %}
                (<a href="/search?p=department_acronym:{{ institution[0] }}&cc=Institutions">{{ institution[0] }}</a>)
              {%endif%}
            {% endif %}
      </h4>
      <div class="row">
        <div class="col-md-12 record-brief-details">
         {% for email in record.get('positions', []) %}
            {% if 'email' in email %}
                {% if email['email']|is_list %}
                  {{ email['email']|email_links|join_array(", ") }}
                {% else %}
                  {{ email['email']|email_links|join_array(", ")|new_line_after }}
                {% endif %}
            {% endif %}
         {% endfor %}
        </div>
      </div>
      <div class="row">
        <div class="col-md-12 record-brief-details">
          {{ record|url_links|join_array(", ")|new_line_after }}
          {% set field_categories = record.get('field_categories', []) %}
          {{ field_categories|join(', ') }}
        </div>
      </div>
    </div>
  </div>
  </div>
  </div>
</div>
{% endblock %}
