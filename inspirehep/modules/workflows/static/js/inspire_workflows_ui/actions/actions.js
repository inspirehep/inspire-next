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
    "js/inspire_workflows_ui/actions/approval_modal",
    "js/inspire_workflows_ui/actions/hep_approval",
    "js/inspire_workflows_ui/actions/literature_approval",
    "js/inspire_workflows_ui/actions/batch_action_hotkeys",
    // "js/inspire_workflows_ui/actions/editable_subjects",
    // "js/inspire_workflows_ui/actions/editable_title",
    // "js/inspire_workflows_ui/actions/editable_urls"
  ],
  function(
    ApprovalModal,
    HepApprovalAction,
    LiteratureApprovalAction,
    BatchActionHotkeys
    // EditableSubjects,
    // EditableTitle,
    // EditableURLs
  ) {

    var attach_action_to = "#workflows-ui-init";

    ApprovalModal.attachTo(document);
    HepApprovalAction.attachTo(document);
    LiteratureApprovalAction.attachTo(document);
    BatchActionHotkeys.attachTo(document);

    // EditableSubjects.attachTo(document, {
    //   edit_url: context.edit_subj_url,
    //   objectid: context.id_object
    // });
    //
    // EditableTitle.attachTo(document, {
    //   edit_url: context.edit_title_url,
    //   objectid: context.id_object
    // });
    //
    // EditableURLs.attachTo(document, {
    //   edit_url: context.edit_urls_url,
    //   objectid: context.id_object
    // });

    console.log("I ran this actions/init.")
  }
);
