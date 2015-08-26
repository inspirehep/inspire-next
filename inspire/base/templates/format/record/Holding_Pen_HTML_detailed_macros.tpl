{#
# This file is part of Inspire.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#}

{% macro add_delimiter(loop, delimiter) %}
  {% if not loop.last %} {{ delimiter }} {% endif %}
{% endmacro %}


{% macro get_subject(term) %}
    {% if term.term %}
        <span> {{ term['term'] }}</span>
    {% else %}
        <span> {{ term['value'] }}</span>
    {% endif %}
{% endmacro %}


{% macro get_arxiv_id(record) %}
    {% if ':' in record['report_number'][0]['primary'] %}
        {{ record['report_number'][0]['primary'][6:] }}
    {% else %}
        {{ record['report_number'][0]['primary'] }}
    {% endif %}
{% endmacro %}


{% macro get_abstract(record) %}
    {% if record['abstract'] is mapping %}
       {{ record['abstract']['summary'] }}
    {% else %}
       {{ record['abstract'][0]['summary'] }}
    {% endif %}
{% endmacro %}