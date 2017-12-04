{#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.
#}

{% macro render_record_title(record) %}
  {% if record.titles %}
    {% set title = record.titles[0].title %}
    {% if title | is_upper %}
      {{ title | capitalize }}
    {% else %}
      {{ title }}
    {% endif %}
    {% for subtitle in record['titles.subtitle'] %}
        {% if subtitle | is_upper %}
          : {{ subtitle | capitalize }}
        {% else %}
          : {{ subtitle }}
        {% endif %}
    {% endfor %}
  {% endif %}
{% endmacro%}

{% macro render_author_names(record, author, show_affiliation) %}
  <a{% if author.affiliations|length > 0  and show_affiliation %}
      data-toggle="tooltip"
      data-placement="bottom"
      title="{{ author.get('affiliations')[0]['value'] }}"
    {% endif %}
    href="http://inspirehep.net/author/profile/{{author.full_name}}?recid={{record['control_number']}}" class="no-external-icon">
    {{ author.get('full_name', '') | format_author_name() }}
    {% if author.affiliations|length > 0  and show_affiliation %}
       ({{ author.get('affiliations')[0]['value'] }})
    {% endif %}
  </a>
{% endmacro %}

{% macro render_record_authors(record, is_brief, number_of_displayed_authors=10, show_affiliations=true, collaboration_only=false) %}
  {% set collaboration_displayed = [] %}
  {% if record.collaborations and not record.get('corporate_author') %}
    {% for collaboration in record.collaborations %}
      {% if collaboration['value'] %}
      <a href="/search?p=collaboration:'{{ collaboration['value'] }}'">{{ collaboration['value'] }}</a>
        {% do collaboration_displayed.append(1) %}
      {% endif %}
      {% if not loop.last %}
        and
      {% endif %}
      {% if loop.last %}
        {% if loop.index == 1%}
          Collaboration
        {% else %}
          Collaborations
        {% endif %}
      {% endif %}
    {% endfor %}
    {% if record.authors is defined %}
     ({{ render_author_names(record, record.authors[0], show_affiliation = True) }} <i>et al.</i>)
    {% endif %}
  {% endif %}


  {% if record.authors and not (collaboration_displayed and collaboration_only) %}
    {% set sep = joiner("; ") %}
    {% set authors = record.authors %}
    {% if not collaboration_displayed %}
      {% for author in authors[0:number_of_displayed_authors] %}
        {{ sep() }}
        {{ render_author_names(record, author, show_affiliation = True ) }}
      {% endfor %}
    {% endif %}
    {% if (record.authors | length > number_of_displayed_authors) %}
        {% if is_brief %}
          {% if not collaboration_displayed %}
            <i>et al.</i>
          {% else %}
            ({{ render_author_names(record, authors[0], show_affiliation = True) }} <i>et al.</i>)
          {% endif %}
        {% else %}
          - <i><a id="authors-show-more" class="authors-show-more" data-toggle="modal" href="" data-target="#authors_{{ record['control_number'] }}">
            Show {{ record.authors | count }} authors & affiliations
          </a></i>
        {% endif %}
    {% else %}
        {% if not is_brief and show_affiliations %}
          {% set affiliations_exist = false %}
          {% for author in record.authors %}
            {% if author.get('affiliations') %}
              {% set affiliations_exist = true %}
            {% endif %}
          {% endfor %}
        {% endif %}
        {% if affiliations_exist %}
            - <i><a id="authors-show-more" class="authors-show-more" data-toggle="modal" href="" data-target="#authors_{{ record['control_number'] }}">
              Show affiliations
            </a></i>
        {% endif %}
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
                {{ render_author_names(record, author) }}
                 {% if author.get('affiliations') and not is_brief %}
                  {% if author.get('affiliations') | is_list %}
                    <a href="{{ url_for('inspirehep_search.search', p='"' + author.get('affiliations')[0].value + '"' + "&cc=Institutions") }}">
                      ({{ author.get('affiliations')[0].value }})
                    </a>
                  {% else %}
                    <a href="{{ url_for('inspirehep_search.search', p='"' + author.get('affiliations').value + '"' + "&cc=Institutions") }}">
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
  {% elif record.get('corporate_author') %}
    {{ record.get('corporate_author')|join('; ') }}
  {% endif %}
{% endmacro %}

{% macro record_report_numbers(record) %}
  {% for report_number in record['report_numbers'] %}
    {% if 'value' in report_number %}
      {% if loop.first %}
        Report number:
      {% endif %}
      {{ report_number['value'] }}
      {% if not loop.last %}
        ,
      {% endif %}
    {% endif %}
  {% endfor %}
{% endmacro %}

{% macro record_arxiv(record, is_brief) %}
  {% if record.get('arxiv_eprints') %}
    {% for report_number in record.get('arxiv_eprints') %}
      {% if is_brief %}
        e-Print:<a href="http://arxiv.org/abs/{{ report_number.get('value') }}" > {{ report_number.get('value') }}</a>
        {% if report_number.get('categories') %}
          [{{ report_number.get('categories')[0] }}]
        {% endif %}
      {% else %}
        <span class="eprint">e-Print</span>
        <a href="http://arxiv.org/abs/{{ report_number.get('value') }}" title="arXiv" target="_blank">{{ report_number.get('value') }}</a>
        {% if report_number.get('categories') %}
          [{{ report_number.get('categories')[0] }}]
        {% endif %}
      {% endif %}
    {% endfor %}
  {% endif %}
{% endmacro %}

{% macro mathjax() %}
<script type="text/javascript"
   src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.2/MathJax.js?config=TeX-AMS-MML_HTMLorMML">
</script>
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
      })
    }
  );
</script>
{% endmacro %}
