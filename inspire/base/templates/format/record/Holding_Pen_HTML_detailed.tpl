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
{% block details_page %}

<!-- Title -->
<h4 id='editable-title'>
  <a href='#' id='edit-title'><i class='fa fa-pencil-square-o'></i></a>
  <strong>
    <span id='title-text'>{{ record['title']['title'] }}</span>
  </strong>
</h4>

<!-- Authors -->
{% for author in record['authors'] %}
  <span>{{ author['full_name'] }}</span>
{% endfor %}

{% endblock %}