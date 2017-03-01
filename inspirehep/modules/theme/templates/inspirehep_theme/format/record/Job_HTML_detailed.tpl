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

{% extends "inspirehep_theme/format/record/Inspire_Default_HTML_detailed.tpl" %}

{% set title=record.title %}

{% block body %}
<ul class="breadcrumb detailed-record-breadcrumb">
<li>
  <span class="fa fa-chevron-left"></span>
  {{ request.headers.get('referer', '')|back_to_search_link("jobs") }}
</li>
</ul>
<div id="record_content">
  <div class="record-detailed record-detailed-jobs">
    <div class="record-header record-header-conference">
    <div class="row row-with-map">
      <div class="col-md-8">
        <div class="record-detailed-information">
          <h1 class='record-detailed-title'>
            {{ record.position }}
          </h1>

          <h2 class="record-detailed-subtitle">
            {% if record.rank %}
              {{ record.rank | join(', ') }}
            {% endif %}

            {% if record.institutions %}
              {% for institution in record.institutions %}
                <a href="/search?p=department_acronym:{{ institution }}&cc=Institutions">
                  {{ institution.name }}
                </a>
              {% endfor %}
            {% endif%}
          </h2>

          {% if record.research_area %}
            <div class="detailed-record-field">
              <label>Field of interest:</label> {{ record.research_area | join(', ') }} <br>
            </div>
          {% endif %}

          {% if record.experiments %}
            <div class="detailed-record-field">
              <label>Experiment:</label> {{ record.experiments | join(', ') }}<br>
            </div>
          {% endif %}

          {% if record.regions %}
            <div class="detailed-record-field">
              <label>Region:</label> {{ record.regions | join(', ') }}<br>
            </div>
          {% endif %}

          {% if record.urls %}
            <div class="detailed-record-field">
              <label>More information:</label>
              {% for url in record.urls %}
                <a href="{{ url['value'] }}">
                  {{ url['value'] }}
                </a>
              {% endfor %}
            </div>
          {% endif %}

          {% if record.legacy_creation_date %}
            <div class="detailed-record-field">
              <label>Date added:</label> {{ record.legacy_creation_date | format_date }}
            </div>
          {% endif %}

      </div>


      <div class="detailed-action-bar btn-group">
      <a class="btn custom-btn btn-warning pdf-btn no-external-icon" href="mailto:jobs@inspirehep.net?subject=Remove-listing-{% if record['acquisition_source'] %}{{ record['acquisition_source'][0]['submission_number']}} {% endif %}&body=Please remove listing {% if record['acquisition_source'] %}{{ record['acquisition_source'][0]['submission_number']}} {% endif %} https://inspirehep.net/jobs/{{ record['control_number'] }}/edit" role="button" title="Remove this listing">Remove this listing</a>
      </div>

      </div>

      <div class="col-md-4 hidden-xs hidden-sm" id="record-detailed-jobs-deadline">
        {% if record.institutions[0].name %}
          <div class="detailed-map" id="job-detailed-map">
            <script>
              function initMap() {
                var mapDiv = document.getElementById('job-detailed-map');
                var address = '{{ record.institutions[0].name }}';
                var geocoder = new google.maps.Geocoder();
                var map = new google.maps.Map(mapDiv, {
                  zoom: 5,
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
                });
                geocodeAddress(geocoder, map, address);
              }
              function geocodeAddress(geocoder, resultsMap, address) {
                geocoder.geocode({'address': address}, function(results, status) {
                  if (status === google.maps.GeocoderStatus.OK) {
                    resultsMap.setCenter(results[0].geometry.location);
                    var image = {
                      url: '/static/images/map/marker-institutions.png',
                      scaledSize: new google.maps.Size(25, 25)
                    };
                    var marker = new google.maps.Marker({
                      map: resultsMap,
                      position: results[0].geometry.location,
                      icon: image
                    });
                  } else {
                    console.error('Geocode was not successful for the following reason: ' + status);
                  }
                });
              }
            </script>
            <script src="https://maps.googleapis.com/maps/api/js?callback=initMap" async defer></script>
            </div>
        {% endif %}
      </div>

      {% if record.closed_date %}
        <div class="detailed-jobs-information">
          Deadline: {{record.closed_date | format_date }}
        </div>
      {% endif %}
    </div>
  </div>
    <div class="row">
      <div class="col-md-8" id="record-detailed-jobs-description">
        <div class="panel">
          <div class="panel-heading">
            Job description
          </div>
          <div class="panel-body">
            {% if record.description %}
              <div class="detailed-jobs-information">
                {{ record.description }}
              </div>
            {% endif %}
          </div>
        </div>
      </div>
      <div class="col-md-4" id="record-detailed-jobs-sidebox">
        <div class="panel">
        <div class="panel-body">
        <div id="record-detailed-jobs-applications">
          <div class="record-detailed-title">
            Applications
          </div>
          {% if record.deadline_date %}
          <div class="detailed-record-field">
            <div class="alert alert-info" id="detailed-jobs-deadline-alert" role="alert">
              Deadline: {{ record.deadline_date | format_date }}
            </div>
          </div>
          {% endif %}
          {% if record.contact_details %}
            <div class="detailed-jobs-information">
              Contact: {{ record.contact_details[0].name }}
            </div>
          {% endif %}
          {% if record.contact_details %}
            <div class="detailed-jobs-information">
              Email: {{ record.contact_details[0].email | email_links | join(', ') }}
            </div>
          {% endif %}
          {% if record.reference_email %}
            <div class="detailed-jobs-information">
              Letters of Reference should be sent to:
              {{ record.reference_email | email_links | join(', ') }}
            </div>
          {% endif %}
        </div>

      </div>
      </div>

      <div class="panel">
        <div class="panel-body">
        <div id="record-detailed-similar-jobs">
          <div class="record-detailed-title">
            Similar Jobs
          </div>
          {% for job in record.similar %}
            <div class="similar-jobs">
              {% if job.ranks %}
                <b>{{ job.ranks[0] }}</b>
              {% endif %}
              <br/>
              <a href="/jobs/{{ job.control_number }}">{{ job.position }}</a>
              <br/>
              {{ record.institutions[0].name }}
              <br/>
              Deadline: {{ job.deadline_date | format_date }}
            </div>
          {% endfor %}
        </div>

      </div>
      </div>

      </div>

    </div>
  </div>
</div>
{% endblock %}
