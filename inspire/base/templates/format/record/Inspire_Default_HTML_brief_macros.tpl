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

{% macro record_info() %}
  {% if record.get('doi')| is_list() %}
  {% set filtered_doi = record.get('doi.doi')| remove_duplicates() %}
  {% for doi in filtered_doi %}
  {% if not doi|has_space() %}    
    <a href="http://dx.doi.org/{{ doi |trim()|safe}}" title="DOI" >{{ doi }}</a><br/>
  {% endif %}
  {% endfor %}
  {% else %}
   <a href="http://dx.doi.org/{{ record.get('doi') }}" title="DOI" >{{ record.get('doi.doi') }}</a><br/>
  {% endif %}
{% endmacro %}

{% macro record_journal_info() %} 
  {% if record.get('publication_info')|is_list() %}
    {% for pub_info in record.get('publication_info')%}
      {% if pub_info.get('journal_title') and pub_info.get('journal_volume') and  pub_info.get('year') and pub_info.get('page_artid') %}
      <span class="text-left"><b><i>{{ pub_info.get('journal_title') }}</i> {{ pub_info.get('journal_volume') }} ({{pub_info.get('year')}}), {{ pub_info.get('page_artid') }}</b></span><br/>
      {% endif %}
    {% endfor %}
    {% else %}
      {% if record.get('publication_info').get('journal_title') and record.get('publication_info').get('journal_volume') and  record.get('publication_info').get('year') and record.get('publication_info').get('page_artid') %}
      <span class="text-left"><b><i>{{ record.get('publication_info').get('journal_title') }}</i> {{ record.get('publication_info').get('journal_volume') }} ({{record.get('publication_info').get('year')}}), {{ record.get('publication_info').get('page_artid') }}</b></span><br/>
    {% endif %}
  {% endif %}
{% endmacro %}

{% macro record_abstract() %}
  {% set exists = [] %}
  {% if record.get('report_number') %}
  {% if record.get('report_number') | is_list() %}
  {% for i in record.get('report_number') %}
  {% if i.get('source') == 'arXiv' %}
  {% do exists.append(1) %}
  {% endif %}
  {% endfor %}
  {% endif %}
  {% endif %}
  {% if record.get('abstract') %}
  {% if record.get('abstract')|is_list() %}
  {% for source in record.get('abstract') %}
    {% if source.get('summary') %}
      <div class="abstract" id="main{{ record.get('_id') }}">{{ source.get('summary')|words(50)|e }}<span id="dots{{ record.get('_id') }}">...</span>
        <a class="expand" id="{{ record.get('_id') }}"  data-toggle="collapse" href="#more{{ record.get('_id') }}" aria-expanded="false" onclick="functions.changeArrow('{{ record.get('_id') }}','arrow_down{{ record.get('_id') }}','arrow_up{{ record.get('_id') }}')"> 
        <i class="fa fa-arrow-down" id="arrow_down{{ record.get('_id') }}"></i>
        <i class="fa fa-arrow-up" id="arrow_up{{ record.get('_id') }}"></i>
        </a>
      </div>
      <div id="more{{ record.get('_id') }}" class="collapse">{{ source.get('summary')|words(50)|e }}</div>
    {% endif %}
  {% endfor %}
  {% endif %}
  {% endif %}
{% endmacro %}
