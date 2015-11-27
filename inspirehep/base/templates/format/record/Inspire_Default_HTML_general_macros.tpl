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

{% macro render_author_names(author, show_affiliation) %}
  <a{% if author.affiliations|length > 0  and show_affiliation %}
      data-toggle="tooltip"
      data-placement="bottom"
      title="{{ author.get('affiliations')[0]['value'] }}"
    {% endif %}
    href="http://inspirehep.net/author/profile/{{author.full_name}}?recid={{record['control_number']}}">
    {{ author.get('full_name') }}
  </a>
{% endmacro %}

{% macro render_record_authors(is_brief, number_of_displayed_authors=10, show_affiliations=true) %}
  {% if record.authors %}
    {% set sep = joiner("; ") %}
    {% set authors = record.authors %}
      {% for author in authors[0:number_of_displayed_authors] %}
        <small>{{ sep() }}</small>
        <small class="text-left">{{ render_author_names(author, show_affiliation = True ) }}</small>
      {% endfor %}
    {% if (record.authors | length > number_of_displayed_authors) %}
      <small>
        {% if is_brief %}
          <i>et al.</i>
        {% else %}
          <a id="authors-show-more" class="text-muted" data-toggle="modal" href="" data-target="#authors_{{ record['control_number'] }}">
            Show {{ record.authors | count }} authors & affiliations
          </a>
        {% endif %}
      </small>
    {% else %}
      <small>
        {% if not is_brief and show_affiliations %}
          <a id="authors-show-more" class="text-muted" data-toggle="modal" href="" data-target="#authors_{{ record['control_number'] }}">
            Show affiliations
          </a>
        {% endif %}
      </small>
    {% endif %}

    {% if show_affiliations %}
      <div class="modal fade authors-modal" id="authors_{{ record['control_number'] }}" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
              <h4 class="modal-title" id="myModalLabel">Authors</h4>
            </div>
            <div class="modal-body">
              {% for author in record.authors %}
                {{ render_author_names(author) }}
                 {% if author.get('affiliations') and not is_brief %}
                  {% if author.get('affiliations') | is_list %} 
                    <a href="{{ url_for('search.search', p='"' + author.get('affiliations')[0].value + '"' + "&cc=Institutions") }}">
                      ({{ author.get('affiliations')[0].value }})
                    </a>
                  {% else %}
                    <a href="{{ url_for('search.search', p='"' + author.get('affiliations').value + '"' + "&cc=Institutions") }}">
                      ({{ author.get('affiliations').value }}) 
                    </a>
                  {% endif %} 
                {% endif %}
                {{ sep() }}
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

{% macro record_abstract(is_brief) %}
  {% if is_brief %}
    {% set number_of_words = 30 %}
  {% else %}
    {% set number_of_words = 100 %}
  {% endif %}
  {% set abstract_displayed = [] %}
  {% set arxiv_abstract = [] %}
  {% if record.get('abstracts') %}
    {% for abstract in record.get('abstracts') %}
      {% if abstract.get('value') and not abstract_displayed %}
        {% if not abstract.get('source') == 'arXiv' %}
          {{ display_abstract(abstract.get('value'), number_of_words) }}
          {% do abstract_displayed.append(1) %}
        {% else %}
          {% do arxiv_abstract.append(abstract.get('value')) %}
        {% endif %}
      {% endif %}
    {% endfor %}
      {% if not abstract_displayed and arxiv_abstract %}
        {{ display_abstract(arxiv_abstract[0], number_of_words) }}
        {% do abstract_displayed.append(1) %}
      {% endif %}
  {% endif %}

  {% if not is_brief and not abstract_displayed %}
      No abstract available for this record
  {% endif %}
{% endmacro %}

{% macro display_abstract(abstract, number_of_words) %}
  <div class="abstract">
    <input type="checkbox" class="read-more-state" id="abstract-input-{{ record.get('control_number') }}" />
    <div class="read-more-wrap">
      {{ abstract | words(number_of_words)| e }}
      <span class="read-more-ellipsis">...</span>
      <span class="read-more-target">
        {{ abstract | words_to_end(number_of_words)| e }}
      </span>
    </div>
    <label for="abstract-input-{{ record.get('control_number') }}" class="read-more-trigger"></label>
  </div>
{% endmacro %}

{% macro record_arxiv(is_brief) %}
  {% if record.get('arxiv_eprints') %}
    {% for report_number in record.get('arxiv_eprints') %}
      {% if is_brief %}
        <div class="eprint">e-Print: 
          <a href="http://arxiv.org/abs/{{ report_number.get('value') }}" > {{ report_number.get('value') }}</a>
        </div>
      {% else %}
        <span class="eprint">e-Print</span>
        <a href="http://arxiv.org/abs/{{ report_number.get('value') }}" title="arXiv" target="_blank">{{ report_number.get('value') }} <i class="fa fa-external-link"></i></a>
      {% endif %}
    {% endfor %}
  {% endif %}
{% endmacro %}

{% macro record_cite_modal() %}
  <!-- MODAL -->
  <div class="modal fade" id="citeModal{{record['control_number']}}" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
    <div class="modal-dialog cite-modal">
      <div class="modal-content">
        <div class="modal-header">
          <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
          <h4 class="modal-title" id="citeModalLabel">Cite Article</h4>
          <div class="btn-group">
            <button type="button" class="btn btn-primary dropdown-toggle" id="btn-drop" data-toggle="dropdown" aria-expanded="false">
              Format: <span id="format{{record['control_number']}}"></span> <span class="caret"></span>
            </button>
            <ul class="dropdown-menu" role="menu">
              <li><a class="pointer bibtex" id="bibtex{{record['control_number']}}" data-recid="{{record['control_number']}}">BibTex</a></li>
              <li><a class="pointer latex_eu" id="latex_eu{{record['control_number']}}" data-recid="{{record['control_number']}}">LaTex(EU)</a></li>
              <li><a class="pointer latex_us" id="latex_us{{record['control_number']}}" data-recid="{{record['control_number']}}">LaTex(US)</a></li>
            </ul>
          </div>
          <a type="button" id="download{{record['control_number']}}" class="btn btn-primary">Download</a>
        </div>
        <div class="modal-body">
          <div class="row">
            <div class="col-md-12">
              <div class="editable" contenteditable="true" onclick="document.execCommand('selectAll',false,null)"><pre id="text{{record['control_number']}}"></pre></div>
            </div>
          </div> 
        </div>
        <div class="modal-footer">
        </div>
      </div>
    </div>
  </div>
  <!-- END MODAL -->
{% endmacro %}

{% macro mathjax() %}
{% set version = '2.5.3' %}
<script src="//cdnjs.cloudflare.com/ajax/libs/mathjax/{{version}}/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>
<script type="text/javascript">
    require([
      "jquery",
      ], function ($) {
          $(document).ready(function () {
            MathJax.Hub.Config({
                tex2jax: {inlineMath: [['$', '$'], ['\\(', '\\)']],
                processEscapes: true},
                showProcessingMessages: false,
                messageStyle: "none"
            });
            MathJax.Hub.Queue(["Typeset", MathJax.Hub]);
          })
      }
    );
</script>
{% endmacro %}