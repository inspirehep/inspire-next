/**
 * Created by eamonnmaguire on 01/06/2016.
 */

(function (angular) {

  function HoldingPenSelectionCtrl($scope) {

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

    $scope.$on('invenio.search.success', reset);
  }

  HoldingPenSelectionCtrl.$inject = ['$scope'];

  angular.module('holdingpen.controllers', [])
    .controller('HoldingPenSelectionCtrl', HoldingPenSelectionCtrl);

})(angular);
