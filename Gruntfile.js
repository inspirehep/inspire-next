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

  var globalConfig = {
    bower_path: 'bower_components',
    installation_path: 'inspire/base/static'
  };

  // show elapsed time at the end
  require('time-grunt')(grunt);
  // load all grunt tasks
  require('load-grunt-tasks')(grunt);

  // Project configuration
  grunt.initConfig({

    pkg: grunt.file.readJSON('package.json'),
    globalConfig: globalConfig,

    less: {
      development: {
        options: {
          compress: true,
          yuicompress: true,
          optimization: 2
        },
        files: {
          // target.css file: source.less file
          "<%= globalConfig.installation_path %>/css/inspire.css": "<%= globalConfig.installation_path %>/less/inspire.less"
        }
      }
    },
    watch: {
      styles: {
        // Which files to watch (all .less files recursively in the less directory)
        files: ['inspire/base/static/less/**/*.less'],
        tasks: ['less'],
        options: {
          nospawn: true
        }
      }
    },
    // copy bootstrap core to make it customizable later
    copy:{
      fonts: {
        expand: true,
        flatten: true,
        cwd: '<%= globalConfig.bower_path %>/bootstrap/',
        src: ['fonts/*'],
        dest: '<%= globalConfig.installation_path %>/bootstrap/fonts/'
      },
      js: {
        expand: true,
        flatten: true,
        cwd: '<%= globalConfig.bower_path %>/bootstrap/',
        src: ['js/*'],
        dest: '<%= globalConfig.installation_path %>/bootstrap/js/'
      },
      less: {
        expand: true,
        flatten: true,
        cwd: '<%= globalConfig.bower_path %>/bootstrap/',
        src: ['less/*'],
        dest: '<%= globalConfig.installation_path %>/bootstrap/less/'
      },
      jquery: {
        expand: true,
        flatten: true,
        cwd: '<%= globalConfig.bower_path %>/jquery/',
        src: ['dist/jquery.min.js'],
        dest: '<%= globalConfig.installation_path %>/js/'
      }
    }
  });

  grunt.registerTask('prod', ['copy', 'less']);
  grunt.registerTask('dev', ['watch']);

};
