{#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#}

{% macro display_collections() %}
  {% if record.get('collections') %}
    {% set collections = record.collections %}
    <span id="{{collections | record_current_collection("Literature") }}">Literature</span>
    <span id="{{collections | record_current_collection("Authors") }}">Authors</span>
    <span id="{{collections | record_current_collection("Conferences") }}">Conferences</span>
    <span id="{{collections | record_current_collection("Jobs") }}">Jobs</span>
  {% endif %}
{% endmacro %}

{% macro collection_header() %}
  {% set collections = record.collections %}
  <div class="collection-header" id="{{collections | record_current_collection("") }}">
    <div class="container">
      {{ display_current_collection() | safe }}
      {{ search_bar() | safe }}
    </div>
  </div>
{% endmacro %}

{% macro display_current_collection() %}
  {% if record.get('collections') %}
    {% set collections = record.collections %}
    {% for collection in collections %}
      {% set collection_name = collection.get('primary') %}
      {{ collection_name | collection_get_title | safe }}
    {% endfor %}
  {% endif %}  
{% endmacro %}

{% macro search_bar() %}
  <div class="search-box pull-right" style="display: inline-block;">
    <form class="search-form" action="/search">
      <input type="text" name="p" placeholder="{{ search_current_collection(is_search=true) | safe | trim }}" value="">
        {% if record.get('collections') %}
          {% set collections = record.collections %}
          <input type="hidden" name="cc" value="{{ collections | return_collection_name | safe }}">
        {% endif %}
    </form>
  </div>
{% endmacro %}

{% macro search_current_collection(is_search) %}
  {% if record.get('collections') %}
  {% set collection_found = [] %}
    {% set collections = record.collections %}
    {% for collection in collections %}
      {% set collection_name = collection.get('primary') %}
      {{ collection_name | search_collection(is_search) | safe }}
    {% endfor %}
  {% endif %} 
{% endmacro %}