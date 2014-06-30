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
   * Imports data using given filter.
   *
   * @param filter {Filter}
   * @returns {Deferred} an object needed for tasks synchronization
   */
  singleImport: function(id, filter) {
    var url = filter.url + id;
    var that = this;

    function processQuery(data) {

      var query_status = data.query ?
        data.query.status : data.status + ' ' + data.statusText;

      if (query_status === 'success' && data.source === 'database') {
        query_status = 'duplicated';
      }

      var queryMessage = that.getImportMessage(query_status, filter.name, id);

      if (query_status !== 'success') {
        return {
          statusMessage: queryMessage
        };
      }

      // do the import
      var depositionType = that.$depositionType.val();
      var mapping = filter.applyFilter(data.query, depositionType);

      return {
        mapping: mapping,
        statusMessage: queryMessage
      };
    }

    return $.ajax({
      url: url
    }).then(processQuery, function onError(data) {
      return {
        statusMessage: {
          state: 'danger',
          message: 'Import from ' + filter.name + ': ' + data.status + ' ' + data.statusText
        }
      };
    });
  },

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

  getSingleImportTask: function(name, id, filter) {
    return {
      name: name,
      fn: this.singleImport,
      args: [
        id,
        filter
      ]
    };
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
  importData: function(arxivId, doi, isbn, on_done) {
    var tasksList = [];
    if (arxivId) {
      tasksList.push(this.getSingleImportTask('arxiv', arxivId, arxivFilter));
    }
    if (doi) {
      tasksList.push(this.getSingleImportTask('doi', doi, doiFilter));
    }
    if (isbn) {
      tasksList.push({
        name: isbn,
        fn: this.isbnImport,
        args: []
      });
    }
    var importer = this;
    this.runMultipleTasks(tasksList, function(results) {
      on_done(importer.mergeSources(results));
    });
  },

  runMultipleTasks: function(tasks, callback) {
    var deferredTasks = [];
    for (var i in tasks) {
      var taskInfo = tasks[i];
      var task = tasks[i].fn.apply(this, tasks[i].args);
      task = this.labelTaskResult(taskInfo.name, task);
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
  mergeSources: function(results) {
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
      mergedMapping = arxivDoiFilter.applyFilter(
        sources, this.$depositionType.val()
    );

    return {
      mapping: mergedMapping,
      statusMessage: messages
    };
  },

  isbnImport: function() {
    return {
      statusMessage: {
        state: 'info',
        message: 'The ISBN importing is not available at the moment.'
      }
    };
  },

  /**
   * Generates the import status message.
   * @param queryStatus
   * @param idType DOI/arXiv/ISBN etc.
   * @param id
   * @returns {{state: string, message: string}} as in the input of
   *  tpl_flash_message template
   */
  getImportMessage: function(queryStatus, idType, id) {
    if (queryStatus === 'notfound') {
      return {
        state: 'warning',
        message: 'The ' + idType + ' ' + id + ' was not found.'
      };
    }
    if(queryStatus === 'malformed') {
      return {
        state: 'warning',
        message: 'The ' + idType + ' ' + id + ' is malformed.'
      };
    }
    if (queryStatus === 'success') {
      return {
        state: 'success',
        message: 'The data was successfully imported from ' + idType + '.'
      };
    }
    if (queryStatus === 'duplicated') {
      return {
        state: 'info',
        message: 'This ' + idType + ' already exists in Inspire database.'
      };
    }

    return {
      state: 'warning',
      message: 'Unknown import result.'
    };
  }
};
