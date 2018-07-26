/*
 * This file is part of INSPIRE.
 * Copyright (C) 2016 CERN.
 *
 * INSPIRE is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of the
 * License, or (at your option) any later version.
 *
 * INSPIRE is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
 * 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
* In applying this license, CERN does not
* waive the privileges and immunities granted to it by virtue of its status
* as an Intergovernmental Organization or submit itself to any jurisdiction.
*/

define(['publications'], function(Publications) {
  var app = angular.module('publications', ['profile']);

  app.directive('publicationsList', function($timeout) {
    return {
      require: '^profileInit',
      restrict: 'E',
      templateUrl: '/assets/js/authors/templates/publications.html',
      scope: true,
      link: function(scope, element) {
        scope.$watch('publications', function() {
          // Inject DataTable.
          $timeout(function() {
            if (scope.publications.length > 0) {
              $('#publications-table').DataTable( {
                'drawCallback': function(settings) {
                  $('[id^=impact-graph-]').each(function() {
                    var _id = $(this).attr('id');
                    if ($(this).html() === '') {
                      var _publication_id = $(this).attr('id').split('-')[2];

                      ImpactGraph.draw_impact_graph(
                        '/api/literature/' + _publication_id,
                        '#impact-graph-' + _publication_id,
                        {
                          width: 150,
                          height: 50,
                          'content-type': 'application/x-impact.graph+json',
                          y_scale: 'linear',
                          render_citations: false
                        }
                      );
                    }
                  })
                },
                'bFilter': false,
                'bLengthChange': false,
                'info' : false,
                // In case of enabled search box.
                'oLanguage': {
                  'sSearch': '<i class="fa fa-search" aria-hidden="true"></i>'
                 }
              });
            }
          }, 0);
        });
      }
    };
  });

  app.directive('impactGraph', function($timeout) {
    return {
      require: '^profileInit',
      restrict: 'E',
      template: '<div id="impact-graph-{{ publication.id }}"></div>',
    };
  });
});
