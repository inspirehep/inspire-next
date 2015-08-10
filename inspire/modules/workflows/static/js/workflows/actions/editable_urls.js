/*
 * This file is part of Invenio.
 * Copyright (C) 2015 CERN.
 *
 * Invenio is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of the
 * License, or (at your option) any later version.
 *
 * Invenio is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Invenio; if not, write to the Free Software Foundation, Inc.,
 * 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
 */


define(
  [
    'jquery',
    'flight/lib/component',
    'hgn!js/workflows/templates/editable_urls',
    'hgn!js/workflows/templates/editable_urls_input',
    'hgn!js/workflows/templates/editable_urls_after_edit',
    'hgn!js/workflows/templates/saving_spinner'
  ],
  function(
    $,
    defineComponent,
    tpl_edit_urls,
    tpl_edit_urls_input,
    tpl_after_edit_urls,
    tpl_spinner) {

    'use strict';

    return defineComponent(EditableURLs);

    function EditableURLs() {

      this.attributes({
        // On init
        editSelector: "#edit-urls",
        modalSelector: "#edit-urls-modal",
        urlContainerSelector: "#url-container",
        urlLinksSelector: "#url-links",

        // After modal appears
        inputsSelector: ".edit-url-input",
        deleteUrlSelector: ".delete-url",
        addNewUrlSelector: "#add-new-url",
        urlInputsSelector: "#urls",
        saveChangesSelector: "#save-changes",

        // URLS
        urls: [],
        edit_url: "",
        objectid: ""
      });

      this.getURLs = function() {
        var urls = [];
        $(this.attr.urlContainerSelector + " a").each(function() {
          // check for the edit button 'a' tag and potential empty inputs
          var url = $(this).text();
          if (url.length) urls.push(url);
        });

        this.attr.urls = urls;
        return urls;
      };

      this.processUrls = function() {
        // We need to check if the urls start with http,
        // or else the links will not work.
        var that = this;
        $(this.attr.urls).each(function(index, url) {
          if (url.indexOf('https://') == -1 && url.indexOf('http://') == -1) {
            that.attr.urls[index] = 'http://' + url;
          }
        });
        return this.attr.urls;
      };

      this.createPayloadForEdit = function() {
        return {
          "objectid": this.attr.objectid,
          "urls": this.processUrls()
        };
      };

      this.addUrlsToPage = function() {
        var that = this;
        $(this.attr.urlLinksSelector).replaceWith(
          tpl_after_edit_urls({urls: that.attr.urls})
        );
      };




      this.makeEditable = function() {
        // Create the modal
        $(this.attr.modalSelector).replaceWith(tpl_edit_urls({
          urls: this.getURLs()
        }));

        var that = this;
        var newUrlList = [];
        $(this.attr.modalSelector)
          .modal('show')

          // Delete the url
          .on('click', this.attr.deleteUrlSelector, function(ev) {
            var urls = that.attr.urls;

            // Remove from url array
            urls.splice(urls.indexOf($(ev.target).prev().val()), 1);
            // Remove div from modal
            $(ev.target).parent().remove();
          })

          // Create new url input
          .on('click', this.attr.addNewUrlSelector, function(ev) {
            $(that.attr.urlInputsSelector).append(tpl_edit_urls_input());
            $(that.attr.urlInputsSelector + " input:last").focus();
          })

          // Save urls in list
          .on('click', this.attr.saveChangesSelector, function(ev) {
            $(that.attr.inputsSelector).each(function(index, element) {
              if (element.value.length) newUrlList.push(element.value);
            });

            that.attr.urls = newUrlList;
            that.makePostRequest();
            that.addUrlsToPage();
          });
      };

      this.makePostRequest = function() {
        var that = this;

        // Add spinner on save button
        $(this.attr.saveChangesSelector).replaceWith(tpl_spinner());
        $.ajax({
          type: "POST",
          url: that.attr.edit_url,
          data: that.createPayloadForEdit(),
          success: function(data) {
            that.trigger(document, "updateAlertMessage", {
              category: data.category,
              message: data.message
            });
          },
          complete: function() {
            $(that.attr.modalSelector).modal("hide");
          }
        });
      };

      this.after('initialize', function() {
        this.on(this.attr.editSelector, 'click', this.makeEditable);
        console.log("Editable URLs OK");
      });
    }
  }
);