{#
## This file is part of INSPIRE.
## Copyright (C) 2015 CERN.
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

{% extends "format/record/Default_HTML_detailed.tpl" %}

{% block header %}
<div class="row">
  <div class="col-md-12">
    <h3>
    {% for collection in record['collections'] %}
      {% if 'primary' in collection %}
        <span class="label label-default pull-left {% if not loop.first %} collection-primary {% endif %}">
        {{ collection['primary'] }}</span>
      {% endif %}
    {% endfor %}
    </h3>
  </div>
</div>
<div class="row"><div class="col-md-12"><p></p></div></div>
<div class="row">
  <div class="col-md-12">
    <div class="pull-left">
      <b>
      {{ record['title'] }}
      </b>
    </div>
  </div>
</div>
<div class="row">
  <div class="col-md-12">
    <div class="pull-left">
      {{ record['short_title'] }}
    </div>
  </div>
</div>
{% if record['urls'] %}
{% for url in record['urls'] %}
<div class="row">
  <div class="col-md-12">
    <div class="pull-left">
      {{ url['urls']|urlize }} 
      {% if url['doc_string'] %}
        ({{ url['doc_string']}})
      {% endif %}
   </div>
  </div>
</div>
{% endfor %}
{% endif %}
<div class="row"><div class="col-md-12"><p></p></div></div>
<div class="row"><div class="col-md-12"><p></p></div></div>
<div class="row">
  <div class="col-md-12">
    <div class="pull-left">
      <a href="/search?p=journal_title:{{ record['short_title'] }}&cc=Hep">Articles in HEP</a>
   </div>
  </div>
</div>
<div class="row"><div class="col-md-12"><p></p></div></div>
<div class="row"><div class="col-md-12"><p></p></div></div>
{% if record['coden'] %}
<div class="row">
  <div class="col-md-12">
    <div class="pull-left">
      {{ record['coden'] }}
   </div>
  </div>
</div>
{% endif %}
{% if record['name_variants'] %}
<button type="button" class="btn btn-default pull-left" data-toggle="modal" data-target="#showNameVariants">
  Show name variants
</button>
{% endif %}
<!-- Modal -->
<div class="modal fade" id="showNameVariants" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">
  <div class="modal-dialog" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
        <h4 class="modal-title" id="myModalLabel">Name variants</h4>
      </div>
      <div class="modal-body">
        <div style="text-align:left;">
        {{ record['name_variants']|join(', ')}}
        </div>
      </div>
      <div class="modal-footer">
      </div>
    </div>
  </div>
</div>
{% endblock %}
{% block details %}
{% endblock %}