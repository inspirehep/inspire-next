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

{% extends "inspirehep_theme/format/record/Base_HTML_brief.tpl" %}

{# Title #}
{% block title_body scoped %}
  <a class="name" href="{{ url_for('invenio_records_ui.recid', pid_value=record['control_number']) }}">
    {{ record.get('name').get('preferred_name', 'value')[0] }}
  </a>

  {% set institution = [] %}
    {% if record['positions'] %}
      {% for position in record['positions'] %}
        {% if position.get('institution', {}).get('name') %}
          {% do institution.append(position.get('institution', {}).get('name')) %}
        {% endif %}
      {% endfor %}
    {% if institution %}
      (<a href="/search?p=department_acronym:{{ institution[0] }}&cc=Institutions">{{ institution[0] }}</a>)
    {% endif %}
  {% endif %}
{% endblock %}

{# E-mail #}
{% block brief_detailes_body_1 scoped %}
  {% for email in record.get('positions', []) %}
    {% if 'email' in email %}
      {% if email['email']|is_list %}
        {{ email['email'] }}
      {% else %}
        {# Literally the food for spambots #}
        <a href="mailto:{{ email['email'] }}">{{ email['email'] }}</a></br>
      {% endif %}
    {% endif %}
  {% endfor %}
{% endblock %}

{# Field categories #}
{% block brief_detailes_body_2 scoped %}
  {% set field_categories = record.get('field_categories', []) %}
  {{ field_categories|join(', ') }}
{% endblock %}
