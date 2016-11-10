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

define(['inspire_results'], function() {
  var app = angular.module('inspire_results', []);

  app.controller('InspireResultsController', ['$scope', '$element', '$attrs',
      function($scope, $element, $attrs) {

    $scope.is_authenticated = $attrs.isAuthenticated
    $scope.user_roles = $attrs.userRoles
    $scope.can_view_editor = can_view_editor()
    $scope.show_tools = show_tools

    function show_tools() {
      return [$scope.can_view_editor].some(function(value) {
        return value === true;
      });
    }

    function can_view_editor() {
      if ($scope.is_authenticated) {
        if
          (
            (-1 !== $scope.user_roles.indexOf('cataloger')) ||
            (-1 !== $scope.user_roles.indexOf('superuser'))
          ) {
          return true;
        }
      }
      return false;
    }
  }]);

  app.directive('inspireResultsInit', function() {
    return {
      restrict: 'A',
      scope: true,
      controller: 'InspireResultsController'
    };
  });
});
