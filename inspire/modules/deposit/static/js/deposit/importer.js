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

function Importer($depositionType) {

  this.$depositionType = $depositionType;
}

Importer.prototype = {

  /**
   * Labels result of a task, the result is following:
   *  { label: formerResult }
   * @param result
   * @returns {{}}
   */
  labelTaskResult: function(label, deferredTask) {

    /**
     * Takes an object adds property 'label' to it
     * @param result
     * @returns {{}}
     */
    function labelObj(obj) {
      obj.label = label;
      return obj;
    }

    // if deferredTask is not a Deferred object returns just the labeled object
    try {
      return deferredTask.then(labelObj);
    } catch(err) {
      return labelObj(deferredTask);
    }
  },

  /**
   * Imports data from multiple sources.
   *
   * @param arxivId
   * @param doi
   * @param isbn
   * @param on_done - callback on done, which receives imported and merged data
   *  as an argument
   */
  importData: function(importTasks, mergeMapper, on_done) {
    var importer = this;
    this.runMultipleTasks(importTasks, function(results) {
      on_done(importer.mergeSources(results, mergeMapper));
    });
  },

  runMultipleTasks: function(tasks, callback) {
    var deferredTasks = [];
    for (var i in tasks) {
      var taskInfo = tasks[i];
      var task = tasks[i].run();
      task = this.labelTaskResult(taskInfo.dataSource.id, task);
      deferredTasks.push(task);
    }
    $.when.apply(this, deferredTasks).then(function() {
      callback(arguments);
    }, function() {
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
    var sources = {}, mergedMapping = {};
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

    if (Object.keys(sources).length)
      mergedMapping = mergeMapper.map(
        sources, this.$depositionType.val()
    );

    return {
      mapping: mergedMapping,
      statusMessage: messages
    };
  },
};
