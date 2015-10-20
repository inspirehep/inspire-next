/*
 * This file is part of INSPIRE.
 * Copyright (C) 2014, 2015 CERN.
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

'use strict';

define(
  [
    "js/workflows/actions/approval",
    "js/workflows/actions/core_approval",
    "js/workflows/actions/core_approval_modal",
    "js/workflows/actions/hep_approval",
    "js/workflows/actions/batch_action_hotkeys",
    "js/workflows/actions/editable_subjects",
    "js/workflows/actions/editable_title",
    "js/workflows/actions/editable_urls"
  ],
  function(
    ApprovalAction,
    CoreApprovalAction,
    CoreApprovalModal,
    HepApprovalAction,
    BatchActionHotkeys,
    EditableSubjects,
    EditableTitle,
    EditableURLs) {


    function initialize(context) {
      ApprovalAction.attachTo(context.attach_action_to, {
        action_url: context.action_url
      });

      CoreApprovalAction.attachTo(context.attach_action_to, {
        action_url: context.action_url
      });

      HepApprovalAction.attachTo(context.attach_action_to, {
        action_url: context.action_url
      });

      BatchActionHotkeys.attachTo(context.attach_action_to, {
        action_url: context.action_url
      });

      EditableSubjects.attachTo(document, {
        edit_url: context.edit_subj_url,
        objectid: context.id_object
      });

      EditableTitle.attachTo(document, {
        edit_url: context.edit_title_url,
        objectid: context.id_object
      });

      EditableURLs.attachTo(document, {
        edit_url: context.edit_urls_url,
        objectid: context.id_object
      });

      CoreApprovalModal.attachTo(context.attach_action_to);
      console.log("I ran this actions/init.")
    }

    return initialize;
  }
);
