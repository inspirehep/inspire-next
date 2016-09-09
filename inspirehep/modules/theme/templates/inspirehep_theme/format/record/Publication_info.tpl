{%- macro pub_info(journal_title, journal_volume, year, journal_issue, page_start, page_end, artid, pubinfo_freetext) -%}
  {%- if journal_title -%}
    <i>{{journal_title}}</i>
    {%- if journal_volume -%}
      {{ " " + journal_volume }}
    {%- endif -%}
    {%- if year -%}
      {{ " " + "(" + year + ")" }}
    {%- endif -%}
    {%- if journal_issue -%}
      {{ " " + journal_issue + ", " }}
    {%- endif -%}
    {%- if page_start and page_end -%}
      {{" " + page_start}}-{{page_end}}
    {%- elif page_start -%}
      {{" " + page_start}}
    {%- elif artid -%}
      {{" " + artid}}
    {%- endif -%}
  {%- elif pubinfo_freetext -%}
    {{pubinfo_freetext}}
  {%- endif -%}
{%- endmacro -%}
