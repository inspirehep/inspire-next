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

require.config({
    baseUrl: '/',
    paths: {
        // Invenio
        jquery: 'vendors/jquery/dist/jquery',
        'ui': 'vendors/jquery-ui/ui',
        'jqueryui-timepicker': 'vendors/jqueryui-timepicker-addon/dist',
        'jquery-form': 'vendors/jquery-form/jquery.form',
        'jquery-ui': 'vendors/jquery-ui/jquery-ui.min',
        hgn: 'vendors/requirejs-hogan-plugin/hgn',
        hogan: 'vendors/hogan/web/builds/3.0.2/hogan-3.0.2.amd',
        text: 'vendors/requirejs-hogan-plugin/text',
        flight: 'vendors/flight/lib',
        bootstrap: 'vendors/bootstrap/dist/js/bootstrap',
        'typeahead': 'vendors/typeahead.js/dist/typeahead.bundle',
        // INSPIRE
        'bootstrap-multiselect': 'vendors/bootstrap-multiselect/js/bootstrap-multiselect'
    },
    shim: {
        // Invenio
        'jqueryui-timepicker/jquery-ui-sliderAccess': {deps: ['jquery']},
        'jqueryui-timepicker/jquery-ui-timepicker-addon': {deps: ['jquery', 'ui/slider']},
        'jqueryui-timepicker/i18n/jquery-ui-timepicker-addon-i18n': {deps: ['jqueryui-timepicker/jquery-ui-timepicker-addon']},
        "bootstrap" : { deps :['jquery'] },
        'typeahead': { deps :['jquery'] },
        // INSPIRE
        "bootstrap-multiselect" : { deps :['jquery'],
                                    exports: '$.fn.multiselect' }
    }
})
