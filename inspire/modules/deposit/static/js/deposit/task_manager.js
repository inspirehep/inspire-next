/*
 * This file is part of INSPIRE.
 * Copyright (C) 2014 CERN.
 *
 * INSPIRE is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * INSPIRE is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
 *
 * In applying this licence, CERN does not waive the privileges and immunities
 * granted to it by virtue of its status as an Intergovernmental Organization
 * or submit itself to any jurisdiction.
 */

define(function(require, exports, module) {

  function TaskManager($depositionType) {

    this.$depositionType = $depositionType;
  }

  TaskManager.prototype = {

    /**
     * Runs multiple tasks and merges the results
     *
     * @param tasks - list of tasks to be run
     * @param mergeMapper - mapper (see mapper.js)
     * @param on_done - callback on done, which receives imported and merged data
     *  as an argument
     */
    runMultipleTasksMerge: function(tasks, mergeMapper, on_done) {
      var taskmanager = this;
      this.runMultipleTasks(tasks, function(results) {
        on_done(taskmanager.mergeSources(results, mergeMapper));
      });
    },

    /**
     * Runs multiple tasks asynchronously and executes a callback when they are
     * resolved/rejected
     *
     * @param tasks - list of tasks (see import_task.js for an example)
     * @param callback - callback on done
     */
    runMultipleTasks: function(tasks, callback) {
      var deferredTasks = [];

      $.each(tasks, function(i, task) {
        var deferred_task = task.run();
        deferredTasks.push(deferred_task);
      });

      $.when.apply(this, deferredTasks).then(function() {
        /* Deferred object was resolved */
        callback(arguments);
      }, function() {
        /* Deferred object was rejected */
        callback(arguments);
      });
    },

    /**
     *
     * @param results an array with all the sources to merge; every item in
     * the array is in the following format:
     *  {
     *    label: String,
     *    mapping: {
     *      fieldId: String,
     *      fieldId: String,
     *      fieldId: String
     *    },
     *    queryStatus: {
     *      state: String,
     *      message: String
     *    }
     *  }
     * @returns {
     *    mapping: {
     *      fieldId: String,
     *      fieldId: String,
     *      fieldId: String
     *    },
     *    statusMessage: [
     *      {
     *        state: String,
     *        message: String
     *      },
     *      {
     *        state: String,
     *        message: String
     *      }
     *    ]
     *  }
     *  merged mapping and query messages in an array
     */
    mergeSources: function(results, mergeMapper) {
      var sources = {},
        mergedMapping = {};
      for (var i in results) {
        var taskResult = results[i];
        if (!taskResult.mapping) {
          continue;
        }
        sources[taskResult.label] = taskResult.mapping;
      }
      var messages = $.map(results, function(val) {
        return val.statusMessage;
      });

      if (Object.keys(sources).length) {
        mergedMapping = mergeMapper.map(
          sources, this.$depositionType.val()
        );
      }

      return {
        mapping: mergedMapping,
        statusMessage: messages
      };
    },
  };
  module.exports = TaskManager;
});
