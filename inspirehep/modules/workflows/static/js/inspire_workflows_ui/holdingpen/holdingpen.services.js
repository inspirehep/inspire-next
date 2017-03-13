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
  /**
   * HoldingPenRecordService allows for the getting, update and resolution of
   * workflow records.
   */
  angular.module('holdingpen.services', [])
    .factory("HoldingPenRecordService", ["$http",
        function ($http) {

          return {

            getRecord: function (vm, workflowId) {
              $http.get('/api/holdingpen/' + workflowId).then(function (response) {
                vm.record = response.data;
                if (vm.record._workflow.data_type == 'authors') {
                  $('#breadcrumb').html(vm.record.metadata.name.value);
                } else {
                  $('#breadcrumb').html(vm.record.metadata.titles[0].title.substring(0, 70) + '...');
                }
              }).catch(function (value) {
                vm.ingestion_complete = false;
                alert(value);
              });
            },

            updateRecord: function (vm, workflowId) {
              return $http.post('/api/holdingpen/' + workflowId + '/action/edit', vm.record).then(function (response) {
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
                'value': decision,
                'pdf_upload': vm.pdf_upload,
                'reason': vm.reason
              });

              $http.post('/api/holdingpen/' + workflowId + '/action/resolve', data).then(function (response) {
                vm.ingestion_complete = true;
                var record = vm.record;
                if (!record) record = vm;

                if(!record._extra_data) {
                  record._extra_data = {};
                }

                record._extra_data.user_action = decision;
                record._extra_data._action = null;

              }).catch(function (value) {
                vm.error = value;
              });
            },

            setBatchDecision: function (records, selected_record_ids, decision) {

              for (var record_idx in selected_record_ids) {

                var _id = selected_record_ids[record_idx];
                var _data = JSON.stringify({
                  'value': decision,
                  'id': _id
                });

                $http.post('/api/holdingpen/' + _id + '/action/resolve', _data).then(function (response) {
                  var _data = JSON.parse(response.config.data);
                  for (var record_idx in records) {
                    if (+_data.id === +records[record_idx]._id) {
                      var record_obj = records[record_idx]._source;
                      if(!record_obj._extra_data) {
                        record_obj._extra_data = {};
                      }
                      record_obj._extra_data.user_action = decision;
                      record_obj._workflow.status = 'WAITING';
                    }
                  }
                });
              }
              selected_record_ids = [];
            },

            deleteRecord: function (vm, workflowId, reload) {
              $http.delete('/api/holdingpen/' + workflowId, vm.record).then(function (response) {
                vm.ingestion_complete = true;
                if (reload)
                  window.location = '/holdingpen/list/'
              }).catch(function (value) {
                vm.ingestion_complete = false;
              });
            },

            resumeWorkflow: function (vm, workflowId) {
              $http.post('/api/holdingpen/' + workflowId + '/action/resume').then(function (response) {
                vm.workflow_flag = 'Workflow resumed';
              }).catch(function (value) {
                vm.resumed = false;
              });
            },

            restartWorkflow: function (vm, workflowId) {
              $http.post('/api/holdingpen/' + workflowId + '/action/restart').then(function (response) {
                vm.workflow_flag = 'Workflow restarted';
              }).catch(function (value) {
                vm.restarted = false;
              });
            }
          }
        }
      ]
    )
  ;
}(angular));
