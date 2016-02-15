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

{% extends "inspirehep_theme/format/record/Default_HTML_detailed.tpl" %}

{% macro row(label, value) %}
  {% if value %}
    <tr>
      <td>
        <div class="field_name">{{ label }}:</div>
      </td>
      <td>
        <div class="field_value">{{ value }}</div>
      </td>
    </tr>
  {% endif %}
{% endmacro %}

{% block header %}
  {{ record.get('name', '') }}
{% endblock %}

{% block details %}
  <div class="details-table">
    <table>
      {{ row('Email', record|email_links|join_array(' ')) }}
      {{ row('Field', record.get('field', [])|join_array(' ')) }}
      {{ row('Author profile', record|author_profile|join_array(' ')) }}
      {{ row('Inspire ID', record.get('inspire_id', [])|join_array(' ')) }}
      {{ row('Institute', record|institutes_links|join_array('\n')) }}
    </table>
  </div>
{% endblock %}