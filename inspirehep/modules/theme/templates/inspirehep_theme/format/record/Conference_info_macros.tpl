{#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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


{%- macro conf_with_pub_info(parent_recid, conference_recid, conference_title) -%}
  (<a href="/record/{{ parent_recid }}">Proceedings</a> of <a href="/record/{{ conference_recid }}">
  {{ conference_title }}</a>)
{%- endmacro -%}

{%- macro conf_without_pub_info(parent_recid, conference_recid, conference_title, page_start='', page_end='', artid='') -%}
    Published in <a href="/record/{{ parent_recid }}">proceedings</a> of <a href="/record/{{ conference_recid }}">{{ conference_title }}</a>
  {%- if page_start and page_end -%}
    , pages
  {{ page_start }}-{{ page_end }}
  {%- elif page_start -%}
    , page
  {{ page_start }}
  {%- elif artid -%}
    , article ID
  {{ artid }}
  {%- endif -%}

{%- endmacro -%}

{%- macro conference_only(conference_recid, conference_title, pub_info=false) -%}
  {%- if pub_info -%}
    <br/>
  {%- endif -%}
  Contribution to <a href="/record/{{ conference_recid }}">{{ conference_title }}</a>
{%- endmacro -%}

{%- macro proceedings_only(parent_recid, parent_title, pub_info=false) -%}
  {%- if pub_info -%}
    (<a href="/record/{{ parent_recid }}">Proceedings</a> of {{ parent_title }})
  {%- else -%}
    Published in <a href="/record/{{ parent_recid }}">proceedings</a> of {{ parent_title }}
  {%- endif -%}
{%- endmacro -%}
