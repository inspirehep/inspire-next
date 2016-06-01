/**
 * Created by eamonnmaguire on 01/06/2016.
 */

(function (angular) {
  angular.module('holdingpen.services', [])
      .factory("HoldingPenRecordService", ["$http",
    function ($http) {
      return {
        /**
         * getRecord
         * @param vm
         * @param workflowId
         */
        getRecord: function (vm, workflowId) {
          $http.get('/api/holdingpen/' + workflowId).then(function (response) {
            vm.record = response.data;
            $('#breadcrumb').html(vm.record.metadata.breadcrumb_title);
          }).catch(function (value) {
            vm.ingestion_complete = false;
            alert(value);
          });
        },

        updateRecord: function (vm, workflowId) {
          $http.post('/api/holdingpen/' + workflowId + '/action/edit', vm.record).then(function (response) {
            vm.saved = true;
            vm.update_ready = false;
          }).catch(function (value) {
            vm.saved = false;
            vm.update_ready = true;
            alert('Sorry, an error occurred when saving. Please try again.');
          });
        },

        setDecision: function (vm, workflowId, decision) {
          var data = JSON.stringify({
            'value': decision
          });
          $http.post('/api/holdingpen/' + workflowId + '/action/resolve', data).then(function (response) {
            vm.ingestion_complete = true;
            var record = vm.record;
            if (!record) record = vm;
            record._extra_data.user_action = decision;
            record._extra_data._action = null;

          }).catch(function (value) {
            vm.error = value;
          });
        },

        deleteRecord: function (vm, workflowId) {
          $http.delete('/api/holdingpen/' + workflowId, vm.record).then(function (response) {
            vm.ingestion_complete = true;
          }).catch(function (value) {
            alert(value);
            vm.ingestion_complete = false;
          });
        },

        resumeWorkflow: function (vm, workflowId) {
          $http.post('/api/holdingpen/' + workflowId + '/action/resume').then(function (response) {
            vm.workflow_flag = 'Workflow resumed';
          }).catch(function (value) {
            alert(value);
            vm.resumed = false;
          });
        },

        restartWorkflow: function (vm, workflowId) {
          $http.post('/api/holdingpen/' + workflowId + '/action/restart').then(function (response) {
            vm.workflow_flag = 'Workflow restarted';
          }).catch(function (value) {
            alert(value);
            vm.restarted = false;
          });
        }
      }
    }]
  );
}(angular));
