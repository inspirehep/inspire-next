/*
 * This file is part of INSPIRE.
 * Copyright (C) 2016 CERN.
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

 require(
   [
    "js/inspire_workflows_ui/details/details",
    "js/inspire_workflows_ui/details/details_page",
  ],
  function() {
    // This file is simply here to make sure the above dependencies are
    // properly loaded and ready to be used by inline scripts.
    //
    // Without it, we have to rely on non-anonymous modules.
    console.info("js/inspire_workflows_ui/details/init is loaded");
  }
);
