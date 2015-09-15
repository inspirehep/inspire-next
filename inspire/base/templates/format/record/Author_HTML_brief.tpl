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

{% extends "format/record/Default_HTML_brief_base.tpl" %}

{% block above_record_header %}
{% endblock %}

{% block record_header %}
  <a href="{{ url_for('record.metadata', recid=record['control_number']) }}">
    {{ record.get('name.preferred_name', '') }}
  </a>
  {% if record["positions"] %}
    {% if record["positions"] %}
      {% if record["positions"][0].get("institution", {}).get("name") %}
        ({{record["positions"][0].get("institution", {}).get("name")}})
      {% endif %}
    {% endif %}
  {% endif %}
{% endblock %}

{% block record_info %}
  {{ record|email_links|join_array(", ")|new_line_after }}
  {{ record|url_links|join_array(", ")|new_line_after }}
  {% set field_categories = record.get('field_categories', []) %}
  {% for category in field_categories %}
    {{category["name"]}}
  {% endfor %}
{% endblock %}
