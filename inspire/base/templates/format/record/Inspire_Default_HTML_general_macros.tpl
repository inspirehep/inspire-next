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

{% macro render_record_authors(number_of_displayed_authors) %}
  {% if record.authors %}
  {% set sep = joiner("; ") %}
  {% set authors = record.authors %}
  {% for author in authors[0:number_of_displayed_authors] %}
  <small>{{ sep() }}</small>
  <small class="text-left" ><a {% if author.get('affiliation') %} data-toggle="tooltip" data-placement="bottom" title={% if author.get('affiliation')|is_list() %} "{{ author.get('affiliation')[0] }}" {% else %} "{{ author.get('affiliation') }}" {% endif %} {% endif %} href="{{ url_for('search.search', p='author:"' + author.get('full_name') + '"') }}">
      {{ author.get('full_name') }}
    </a></small>
  {% endfor %}
  {% if record.authors|length > number_of_displayed_authors %}
  {{ sep() }}
  <a href="#authors_{{ record['recid'] }}" class="text-muted" data-toggle="modal" data-target="#authors">
      <em>{{ _(' Show all') }}</em>
  </a>
  <div class="modal fade" id="authors" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
        <h4 class="modal-title" id="myModalLabel">Authors</h4>
      </div>
      <div class="modal-body">
        {% for author in record.authors %}
        <small class="text-left" ><a {% if author.get('affiliation') %} data-toggle="tooltip" data-placement="bottom" title={% if author.get('affiliation')|is_list() %} "{{ author.get('affiliation')[0] }}" {% else %} "{{ author.get('affiliation') }}" {% endif %} {% endif %} href="{{ url_for('search.search', p='author:"' + author.get('full_name') + '"') }}">
         {{ author.get('full_name') }}
        </a></small>
        <small>{{ sep() }}</small>
        {% endfor %}
      </div>
      <div class="modal-footer">
      </div>
    </div>
  </div>
</div>
  {% endif %}
  {% endif %}
{% endmacro %}

{% macro record_arxiv() %}
  {% if record.get('report_number') %}
  {% if record.get('report_number') | is_list() %}
  {% set filtered_arxiv = record.get('report_number')| remove_duplicates_from_dict() %}
  {% for i in filtered_arxiv %}
  {% if i.get('source') == 'arXiv' %}
  <b>e-Print:</b><a href="http://arxiv.org/abs/{{ i.get('primary') }}" > {{ i.get('primary') }}
  </a>
  {% if i.get('arxiv_category') %}
  &nbsp;<b>[{{  i.get('arxiv_category')  }}]</b>
  {% endif %}
  {% endif %}
  {% endfor %}
  {% endif %}
  {% endif %}
{% endmacro %}
