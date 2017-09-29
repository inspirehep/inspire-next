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

{% extends "inspirehep_theme/format/record/Inspire_Default_HTML_detailed.tpl" %}

{% set title=record.title %}

{% block body %}
<ul class="breadcrumb detailed-record-breadcrumb">
<li>
  <span class="fa fa-chevron-left"></span>
  {{ request.headers.get('referer', '')|back_to_search_link("institutions") }}
</li>
</ul>
<div id="record_content">
  <div class="record-detailed record-detailed-institution">
    <div class="record-header record-header-institution">
      <div class="row row-with-map">
        <div class="col-md-8">
          <div class="record-detailed-information">
            <h1 class='record-detailed-title'>
              {% if record['institution'] %}
                {% if record['institution'] | is_list %}
                  {{ record['institution'][0] }}
                {% else %}
                  {{ record['institution'] }}
                {% endif %}
              {% endif %}
            </h1>
            <h2 class="record-detailed-subtitle">
              {% if record['department'] | is_list %}
                {{ record['department'][0] }}
              {% endif %}
            </h2>
            {% if record['urls'] %}
            <div class="detailed-record-field">
              {% for url in record['urls'] %}
                <a href="{{ url['value'] }}">{{ url['value'] }}</a>
                <br>
              {% endfor %}
            </div>
            {% endif %}

            {% if record['name_variants'] %}
              <div class="detailed-record-field">
                {% set name_var = [] %}
                {% for element in record['name_variants'] %}
                  {% if 'source' not in element and 'value' in element %}
                    {% do name_var.append(element['value']) %}
                  {% endif %}
                {% endfor %}
                {% if name_var %}
                  <label>Name variants:</label>
                  {{ name_var[0] | join(', ') }}
                {% endif %}
              </div>
            {% endif %}

            {% if record['public_notes'] %}
              <div class="detailed-record-field">
                <label>Notes:</label>
                {{ record['public_notes'] | join(', ') }}
              </div>
            {% endif %}
          </div>
          {% if record.admin_tools %}
            <div class="col-md-12" id="admin-tools">
              {% for tool in record.admin_tools %}
                {% if tool == 'editor' %}
                  <a href="/editor/institutions/{{record.control_number}}"><i class="fa fa-pencil" aria-hidden="true"></i> Edit</a>
                {% endif %}
              {% endfor %}
            </div>
          {% endif %}
        </div>

        <div class="col-md-4 hidden-xs hidden-sm" id="record-detailed-institution-map">
          <div class="detailed-map" id="institution-detailed-map"></div>
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col-md-12">
        <div class="panel panel-datatables" id="record-institution-papers">
          <div class="panel-heading">Papers</div>

          <div class="panel-body">
            <div class="datatables-loading"> <i class="fa fa-spinner fa-spin fa-lg" ></i>
              <br>Loading papers from institution...</div>
            <div class="datatables-wrapper">
              <table id="record-institution-papers-table" class="table table-striped table-bordered table-with-ellipsis" cellspacing="0" width="100%">
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Authors</th>
                    <th>Journal</th>
                    <th># Citations</th>
                    <th>Year</th>
                  </tr>
                </thead>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col-md-6">
        <div class="panel panel-datatables" id="record-institution-people">
          <div class="panel-heading">Authors</div>
          <div class="panel-body">
            <div class="datatables-loading"> <i class="fa fa-spinner fa-spin fa-lg" ></i>
              <br>Loading authors...</div>
            <div class="datatables-wrapper">
              <table id="record-institution-people-table" class="table table-striped table-bordered" cellspacing="0" width="100%">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th># Papers</th>
                  </tr>
                </thead>
              </table>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="panel panel-datatables" id="record-institution-experiments">
          <div class="panel-heading">Experiments</div>

          <div class="panel-body">
            <div class="datatables-loading">
              <i class="fa fa-spinner fa-spin fa-lg" ></i>
              <br>Loading experiments...</div>
            <div class="datatables-wrapper">
              <table id="record-institution-experiments-table" class="table table-striped table-bordered" cellspacing="0" width="100%">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th># Papers</th>
                  </tr>
                </thead>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
{% endblock %}


{% block additional_javascript %}
<script type="text/javascript" src="//maps.googleapis.com/maps/api/js?key=AIzaSyA0JQa0S94TdFfXHsj7JKXjVN9mu0FighU"></script>
<script>
    google.maps.event.addDomListener(window, 'load', init);

    function init() {
      var mapElement = document.getElementById('institution-detailed-map');
      var doc = {{ record|json_dumps|safe }};
      var address = doc['address'][0]['original_address'].join(', ');
      if ( doc['address'][0]['city'] !== undefined ) {
        address = address + ', ' + doc['address'][0]['city'];
      }

      if ( doc['address'][0]['country'] !== undefined ) {
        address = address + ', ' + doc['address'][0]['country'];
      }

      var institution = doc['ICN'][0];
      var department_html = "";
      if (doc['department'] !== undefined) {
        department_html = '<strong>' + doc['department'][0] + '</strong></br>'
      }

      var geocoder = new google.maps.Geocoder();
      var mapOptions = {
        zoom: 5,
        mapTypeControl: false,
        // Snazzy Map styling.
        styles: [{
            "featureType": "water",
            "elementType": "geometry",
            "stylers": [{"color": "#e9e9e9"}, {"lightness": 17}]
        }, {
            "featureType": "landscape",
            "elementType": "geometry",
            "stylers": [{"color": "#f5f5f5"}, {"lightness": 20}]
        }, {
            "featureType": "road.highway",
            "elementType": "geometry.fill",
            "stylers": [{"color": "#ffffff"}, {"lightness": 17}]
        }, {
            "featureType": "road.highway",
            "elementType": "geometry.stroke",
            "stylers": [{"color": "#ffffff"}, {"lightness": 29}, {"weight": 0.2}]
        }, {
            "featureType": "road.arterial",
            "elementType": "geometry",
            "stylers": [{"color": "#ffffff"}, {"lightness": 18}]
        }, {
            "featureType": "road.local",
            "elementType": "geometry",
            "stylers": [{"color": "#ffffff"}, {"lightness": 16}]
        }, {
            "featureType": "poi",
            "elementType": "geometry",
            "stylers": [{"color": "#f5f5f5"}, {"lightness": 21}]
        }, {
            "featureType": "poi.park",
            "elementType": "geometry",
            "stylers": [{"color": "#dedede"}, {"lightness": 21}]
        }, {
            "elementType": "labels.text.stroke",
            "stylers": [{"visibility": "on"}, {"color": "#ffffff"}, {"lightness": 16}]
        }, {
            "elementType": "labels.text.fill",
            "stylers": [{"saturation": 36}, {"color": "#333333"}, {"lightness": 40}]
        }, {"elementType": "labels.icon", "stylers": [{"visibility": "off"}]}, {
            "featureType": "transit",
            "elementType": "geometry",
            "stylers": [{"color": "#f2f2f2"}, {"lightness": 19}]
        }, {
            "featureType": "administrative",
            "elementType": "geometry.fill",
            "stylers": [{"color": "#fefefe"}, {"lightness": 20}]
        }, {
            "featureType": "administrative",
            "elementType": "geometry.stroke",
            "stylers": [{"color": "#fefefe"}, {"lightness": 17}, {"weight": 1.2}]
        }]
      };
      var map = new google.maps.Map(mapElement, mapOptions);
      var infowindow = new google.maps.InfoWindow({
        pixelOffset: new google.maps.Size(0, -20)
      });

      geocodeAddress(address);

    function geocodeAddress(address) {
      geocoder.geocode({'address': address}, function(results, status) {
        if (status === google.maps.GeocoderStatus.OK) {
          map.setCenter(results[0].geometry.location);
          var image = {
            url: '/static/images/map/marker-institutions.png',
            scaledSize: new google.maps.Size(25, 25)
          };
          var marker = new google.maps.Marker({
            map: map,
            position: results[0].geometry.location,
            icon: image
          });

          infowindow.setContent('<strong>' + institution + '</strong><br/>' +
            department_html +
            '<i>' + address + '</i>');
          infowindow.setPosition(results[0].geometry.location);
          infowindow.open(map);
        } else {
          console.error('Geocode was not successful for the following reason: ' + status);
        }
      });
    }
  }
  </script>
<script type="text/javascript">
    require(
      [
        "js/datatables",
      ],
      function(
        DataTables
      ) {
        DataTables.attachTo(document, {
          'recid': "{{ record.control_number }}"
        });
      });
  </script>
{% endblock %}
