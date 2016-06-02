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
 *
 * In applying this license, CERN does not
 * waive the privileges and immunities granted to it by virtue of its status
 * as an Intergovernmental Organization or submit itself to any jurisdiction.
 */

(function (angular) {

  function HoldingPenSelectionCtrl($scope, Hotkeys) {

    $scope.vm.selected_records = [];

    $scope.toggleSelection = toggleSelection;
    $scope.toggleAll = toggleAll;
    $scope.isChecked = isChecked;
    $scope.allChecked = allChecked;

    function getItemIdx(id) {
      return $scope.vm.selected_records.indexOf(+id);
    }

    function toggleSelection(id) {
      if (isChecked(id)) {
        $scope.vm.selected_records.splice(getItemIdx(+id), 1);
      }
      else {
        $scope.vm.selected_records.push(+id);
      }
    }

    function toggleAll() {

      var remove_all = allChecked();
      if (remove_all) {

        $scope.vm.selected_records = [];
      } else {
        angular.forEach($scope.$parent.vm.invenioSearchResults.hits.hits,
          function (record) {
            if (!isChecked(record._id))
              $scope.vm.selected_records.push(+record._id);

          });
      }
    }

    function isChecked(id) {
      return getItemIdx(+id) !== -1;
    }

    function allChecked() {
      if (!$scope.$parent.vm.invenioSearchResults.hits) {
        return false;
      }
      return $scope.vm.selected_records.length ===
        $scope.$parent.vm.invenioSearchResults.hits.hits.length;
    }

    function reset() {
      $scope.vm.selected_records = [];
    }

    var hotkey = Hotkeys.createHotkey({
      key: 'ctrl+a',
      callback: function () {
        toggleAll();
      }
    });

    Hotkeys.registerHotkey(hotkey);

    $scope.$on('invenio.search.success', reset);
  }

  HoldingPenSelectionCtrl.$inject = ['$scope', 'Hotkeys'];

  angular.module('holdingpen.controllers', [])
    .controller('HoldingPenSelectionCtrl', HoldingPenSelectionCtrl);

})(angular);
