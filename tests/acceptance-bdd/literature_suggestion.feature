# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

Feature: Literature Suggestions
    A web page to submit articles.

  # arXiv text input
  Scenario: Writing the correct arXiv id
    Given I am logged in
    When I go to the literature suggestion page
    And I insert <input> in the input box with id arxiv_id
    Then I should not see the arxiv error message

  Examples: Vertical
    | input | 1001.4538 | hep-th/9711200 |

  Scenario: Writing the wrong arXiv id
    Given I am logged in
    When I go to the literature suggestion page
    And I insert <input> in the input box with id arxiv_id
    Then I should see the arxiv error message

  Examples: Vertical
    | input | hep-th.9711200 |

  # DOI text input
  Scenario: Writing the correct DOI
    Given I am logged in
    When I go to the literature suggestion page
    And I insert <input> in the input box with id doi
    Then I should not see the arxiv error message

  Examples: Vertical
    | input | 10.1086/305772 |

  Scenario: Writing the wrong DOI
    Given I am logged in
    When I go to the literature suggestion page
    And I insert <input> in the input box with id doi
    Then I should see the doi error message

  Examples: Vertical
    | input | dummy:10.1086/305772 | wrong-doi

  # Thesis date text input
  Scenario: Writing a correct thesis date
    Given I am logged in
    When I go to the literature suggestion page
    And I click on the button Skip, and uncollapse all panels
    And I select the value thesis in the select box with id type_of_doc
    And I insert <input> in the input box with id thesis_date
    Then I should not see the date error message

  Examples: Vertical
    | input | 2016-01 | 2016 |

  Scenario: Writing a wrong thesis date
    Given I am logged in
    When I go to the literature suggestion page
    And I click on the button Skip, and uncollapse all panels
    And I select the value thesis in the select box with id type_of_doc
    And I insert <input> in the input box with id thesis_date
    Then I should see the date error message

  Examples: Vertical
    | input | wrong | 2016-02-30 | 2016-13 |

  # URL text input
  Scenario: Writing a correct url
    Given I am logged in
    When I go to the literature suggestion page
    And I click on the button Skip, and uncollapse all panels
    And I insert pdf_url_correct in the input box with id url
    Then I should not see the url error message

  Scenario: Writing a wrong url
    Given I am logged in
    When I go to the literature suggestion page
    And I click on the button Skip, and uncollapse all panels
    And I insert pdf_url_wrong in the input box with id url
    Then I should see the url error message

  # thesis info autocomplete for supervisor institution
  Scenario: Using the autocomplete for the supervisor institution
    Given I am logged in
    When I go to the literature suggestion page
    And I click on the button Skip, and uncollapse all panels
    And I select the value thesis in the select box with id type_of_doc
    And I insert CER in the autocomplete input box with id supervisors-0-affiliation
    Then I should see CERN in the input box with id supervisors-0-affiliation

  # journal info autocomplete for title
  Scenario: Using the autocomplete for the journal title
    Given I am logged in
    When I go to the literature suggestion page
    And I click on the button Skip, and uncollapse all panels
    And I insert Nuc in the autocomplete input box with id journal_title
    Then I should see Nuclear Physics in the input box with id journal_title

  # Conference info autocomplete for title
  Scenario: Using the autocomplete for the conference title
    Given I am logged in
    When I go to the literature suggestion page
    And I click on the button Skip, and uncollapse all panels
    And I insert autrans in the autocomplete input box with id conf_name
    Then I should see IN2P3 School of Statistics, 2012-05-28, Autrans, France in the input box with id conf_name

  # Basic info autocomplete for affiliation
  Scenario: Using the autocomplete for the affilitaion
    Given I am logged in
    When I go to the literature suggestion page
    And I click on the button Skip, and uncollapse all panels
    And I insert oxf in the autocomplete input box with id authors-0-affiliation
    Then I should see Oxford U. in the input box with id authors-0-affiliation

  # Import an article with the arXiv id
  Scenario: Import an article using the arXiv id
    Given I am logged in
    When I go to the literature suggestion page
    And I insert <input> in the input box with id arxiv_id
    And I click on the button with id importData
    And I click on the button with id acceptData
    Then I should see International Journal of Theoretical Physics in the input box with id journal_title
    And I should see 4 in the input box with id issue
    And I should see 1999 in the input box with id year
    And I should see 38 in the input box with id volume
    And I should see 1113-1133 in the input box with id page_range_article_id
    And I should see Maldacena, Juan in the input box with id authors-0-name
    And I should see 10.1023/A:1026654312961 in the input box with id doi
    And I should see The Large N Limit of Superconformal Field Theories and Supergravity in the input box with id title
    And I should see We show that the large $N$ limit of certain conformal field theories in the input box with id abstract

  Examples: Vertical
    | input | hep-th/9711200 |

  # Import an article with the DOI id
  Scenario: Import an article using the DOI id
    Given I am logged in
    When I go to the literature suggestion page
    And I insert <input> in the input box with id doi
    And I click on the button with id importData
    And I click on the button with id acceptData
    Then I should see The Astrophysical Journal in the input box with id journal_title
    And I should see 2 in the input box with id issue
    And I should see 1998 in the input box with id year
    And I should see 500 in the input box with id volume
    And I should see 525-553 in the input box with id page_range_article_id
    And I should see Schlegel, David J. in the input box with id authors-0-name
    And I should see 10.1086/305772 in the input box with id doi
    And I should see Maps of Dust Infrared Emission for Use in Estimation of Reddening and Cosmic Microwave Background Radiation Foregrounds in the input box with id title

  Examples: Vertical
    | input | 10.1086/305772 |

  Scenario: Submit thesis and verify entry in the list page
    Given I am logged in
    When I go to the literature suggestion page
    And I click on the button Skip, and uncollapse all panels
    And I select the value thesis in the select box with id type_of_doc
    And I insert My Title For Test in the input box with id title
    And I select the value Computing in the subject dropdown list
    And I insert Mister White in the input box with id authors-0-name
    And I click on the link with text Add another author
    And I insert Mister Brown in the input box with id authors-1-name
    And I insert Lorem ipsum dolor sit amet, consetetur sadipscing elitr. in the input box with id abstract
    And I click on the submit button
    And I go to the holding panel list page
    Then I should see the record in the list page
    When I click on the link with text Show abstract
    Then I should see Computing in the record entry
    And I should see My Title For Test in the record entry
    And I should see admin@inspirehep.net in the record entry
    And I should see Mister White; Mister Brown in the record entry
    And I should see Lorem ipsum dolor sit amet, consetetur sadipscing elitr. in the record entry

  Scenario: Submit thesis and verify record detail in the Holding Pen
    Given I am logged in
    When I go to the literature suggestion page
    And I click on the button Skip, and uncollapse all panels
    And I select the value thesis in the select box with id type_of_doc
    And I insert My Title For Test in the input box with id title
    And I select the value Computing in the subject dropdown list
    And I insert Mister White in the input box with id authors-0-name
    And I insert Wisconsin U., Madison in the input box with id authors-0-affiliation
    And I insert Lorem ipsum dolor sit amet, consetetur sadipscing elitr. in the input box with id abstract
    And I click on the submit button
    And I go to the holding panel list page
    Then I should see the record in the list page
    When I click on the link with text My Title For Test
    Then I should see Lorem ipsum dolor sit amet, consetetur sadipscing elitr. in the record detail
    And I should see Submitted by admin@inspirehep.net in the record detail
    And I should see Wisconsin U., Madison in the record detail
    And I should see My Title For Test in the record detail
    And I should see Mister White in the record detail
    And I should see Computing in the record detail


  Scenario: Accept thesis and verify the confirmation message
    Given I am logged in
    When I go to the literature suggestion page
    And I click on the button Skip, and uncollapse all panels
    And I select the value thesis in the select box with id type_of_doc
    And I insert My Title For Test in the input box with id title
    And I select the value Computing in the subject dropdown list
    And I insert Mister White in the input box with id authors-0-name
    And I insert Lorem ipsum dolor sit amet, consetetur sadipscing elitr. in the input box with id abstract
    And I click on the submit button
    And I go to the holding panel list page
    Then I should see the record in the list page
    When I click on the link with text My Title For Test
    And I click on the accept button
    Then I should see the message of confirmation


  Scenario: Submit article and verify entry in the list page
    Given I am logged in
    When I go to the literature suggestion page
    And I click on the button Skip, and uncollapse all panels
    And I insert My Title For Test in the input box with id title
    And I select the value Computing in the subject dropdown list
    And I insert Mister White in the input box with id authors-0-name
    And I click on the link with text Add another author
    And I insert Mister Brown in the input box with id authors-1-name
    And I insert Lorem ipsum dolor sit amet, consetetur sadipscing elitr. in the input box with id abstract
    And I click on the submit button
    And I go to the holding panel list page
    Then I should see the record in the list page
    When I click on the link with text Show abstract
    Then I should see Computing in the record entry
    And I should see My Title For Test in the record entry
    And I should see admin@inspirehep.net in the record entry
    And I should see Mister White; Mister Brown in the record entry
    And I should see Lorem ipsum dolor sit amet, consetetur sadipscing elitr. in the record entry

  Scenario: Submit article and verify record detail in the detail page
    Given I am logged in
    When I go to the literature suggestion page
    And I click on the button Skip, and uncollapse all panels
    And I insert My Title For Test in the input box with id title
    And I select the value Computing in the subject dropdown list
    And I insert Mister White in the input box with id authors-0-name
    And I insert Wisconsin U., Madison in the input box with id authors-0-affiliation
    And I insert Lorem ipsum dolor sit amet, consetetur sadipscing elitr. in the input box with id abstract
    And I click on the submit button
    And I go to the holding panel list page
    Then I should see the record in the list page
    When I click on the link with text My Title For Test
    Then I should see Lorem ipsum dolor sit amet, consetetur sadipscing elitr. in the record detail
    And I should see Submitted by admin@inspirehep.net in the record detail
    And I should see Wisconsin U., Madison in the record detail
    And I should see My Title For Test in the record detail
    And I should see Mister White in the record detail
    And I should see Computing in the record detail

  Scenario: Accept article and verify the confirmation message
    Given I am logged in
    When I go to the literature suggestion page
    And I click on the button Skip, and uncollapse all panels
    And I insert My Title For Test in the input box with id title
    And I select the value Computing in the subject dropdown list
    And I insert Mister White in the input box with id authors-0-name
    And I insert Lorem ipsum dolor sit amet, consetetur sadipscing elitr. in the input box with id abstract
    And I click on the submit button
    And I go to the holding panel list page
    Then I should see the record in the list page
    When I click on the link with text My Title For Test
    And I click on the accept button
    Then I should see the message of confirmation
