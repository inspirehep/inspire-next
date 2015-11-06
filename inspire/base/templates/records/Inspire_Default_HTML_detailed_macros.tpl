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

{% macro collection_header() %}
  <div class="collection-header" id="{{ collection.name | sanitize_collection_name()}}-collection">
    <div class="container">
      {{ display_current_collection() | safe }}
      {{ search_bar() | safe }}
    </div>
  </div>
{% endmacro %}

{% macro display_current_collection() %}
  {{ collection.name | get_collection_title | safe }}
{% endmacro %}

{% macro search_bar() %}
  <div class="search-box pull-right" style="display: inline-block;">
    <form class="search-form" action="/search">
      <input type="text" name="p" placeholder="&#xF002; Search {{ collection.name | sanitize_collection_name() }}" value="">
      <input type="hidden" name="cc" value="{{ collection.name }}">
    </form>
  </div>
{% endmacro %}