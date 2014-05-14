/*
** This file is part of INSPIRE.
** Copyright (C) 2014 CERN.
**
** INSPIRE is free software: you can redistribute it and/or modify
** it under the terms of the GNU General Public License as published by
** the Free Software Foundation, either version 3 of the License, or
** (at your option) any later version.
**
** INSPIRE is distributed in the hope that it will be useful,
** but WITHOUT ANY WARRANTY; without even the implied warranty of
** MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
** GNU General Public License for more details.
**
** You should have received a copy of the GNU General Public License
** along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
**
** In applying this licence, CERN does not waive the privileges and immunities
** granted to it by virtue of its status as an Intergovernmental Organization
** or submit itself to any jurisdiction.
*/


/* Extracted from http://stackoverflow.com/a/18006498 */
function parseQueryString(url) {
    var queryStringIdx = url.indexOf('?');
    var pairs = url.substr(queryStringIdx + 1)
                   .split('&')
                   .map(function(p) { return p.split('='); });
    var result = { };
    for (var i = 0; i < pairs.length; i++) {
        result[decodeURIComponent(pairs[i][0])] = decodeURIComponent(pairs[i][1]);
    }

    return result;
}


(function($) {

    /* TODO: refactor! */

    var json, tabsState;
    $('#myTab a[data-toggle="tab"]').on('shown.bs.tab', function(e) {
        var href, json, parentId, tabsState;
        tabsState = localStorage.getItem("tabs-state");
        json = JSON.parse(tabsState || "{}");
        parentId = $(e.target).parents("ul.nav.nav-tabs").attr("id");
        href = $(e.target).attr('href');
        json[parentId] = href;

        // display the options only for the default collection
        if(href=="#Literature") {
            $('#drop').show();
        } else {
            $('#drop').hide();
        }

        return localStorage.setItem("tabs-state", JSON.stringify(json));
    });

    tabsState = localStorage.getItem("tabs-state");
    json = JSON.parse(tabsState || "{}");

    $.each(json, function(containerId, href) {
        return $("#" + containerId + " a[href=" + href + "]").tab('show');
    });

    var href = json.myTab
        , el = $("a[href=" + href + "]")
        , $collection = el.data('cc');

    $('input#collection').val($collection);

    $("ul#myTab").each(function() {
        var $this = $(this);

        // when in homepage go to the default tab
        if (window.location.href.split("/").length < 5 && location.search == "") {
            $('input#collection').val($this.find("a[data-toggle=tab]:first").data('cc'));
            return $this.find("a[data-toggle=tab]:first").tab("show");
        }
    });

    $('#myTab a[data-toggle="tab"]').on('click', function(e){
        e.preventDefault();
        var $this = $(this)
            , $collection = $this.data('cc');

        if ($this.attr('id') != 'hep') {
            $('#drop').hide();
        } else {
            $('#drop').show();
        }

        // send the cc value to the hidden input
        $('input#collection').val($collection);
    });

    // this fix removes the cc parameter when inside default collection
    $( "form#searchform" ).submit(function( event ) {
        if ( $( "input#collection" ).val() === "" ) {
            $("input#collection").prop('disabled', true);
            return;
        }
    });

    // Keep the output format selected based on the URL
    var url_components = parseQueryString(window.location.href);
    if ( url_components.of ) {
        $('select[name=of]>option[value=' + url_components.of + ']').prop('selected', true);
    }
    // Keep the tab selected based on the URL
    if (url_components.cc) {
        $('#myTab a[href="#'+url_components.cc+'"]').tab('show');
    }

})(jQuery);
