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

module.exports = function(grunt) {

  var prefix = process.env.VIRTUAL_ENV || '../..',
        globalConfig = {
          bower_path: 'bower_components',
          installation_path: prefix + '/var/invenio.base-instance/static'
        };

  // show elapsed time at the end
  require('time-grunt')(grunt);
  // load all grunt tasks
  require('load-grunt-tasks')(grunt);

  // Project configuration
  grunt.initConfig({

    pkg: grunt.file.readJSON('package.json'),
    globalConfig: globalConfig,

    copy: {
      js: {
          expand: true,
          flatten: true,
          cwd: '<%= globalConfig.bower_path %>/',
          src: ['buckets/buckets.js',
                  'jquery-feeds/dist/jquery.feeds.min.js',
                  'moment/min/moment.min.js',
                  'bootstrap-multiselect/js/bootstrap-multiselect.js'],
          dest: '<%= globalConfig.installation_path %>/js/'
      },
      css: {
          expand: true,
          flatten: true,
          cwd: '<%= globalConfig.bower_path %>/',
          src: ['bootstrap-multiselect/css/bootstrap-multiselect.css'],
          dest: '<%= globalConfig.installation_path %>/css/'
      }
    },
    jshint: {
      options: {
        curly: true,
        eqeqeq: true,
        eqnull: true,
        browser: true,
        globals: {
          jQuery: true
        }
      },
      all: ['inspire/modules/**/static/js/**/*.js']
    }
  });

  grunt.registerTask('default', ['copy']);

};
