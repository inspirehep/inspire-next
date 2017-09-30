# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
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

"""LaTeX (CV) writer for records."""

from __future__ import absolute_import, division, print_function
from . import LatexWriter


class LatexCVWriter(LatexWriter):
    """
    Writes a pre/post-amble to create a full CV-type document.
    Strings are inline, bacause escaping curly braces in jinja2
    does not increase legibility.
    """

    PREAMBLE = r"""\documentclass{article}
\usepackage{textcomp} % text version of symbols in TS1, e.g. \textrightarrow{}
\usepackage{amstext} % proper support of frequently used \text{} command
\usepackage[utf8]{inputenc} % support for Unicode characters
\newif\ifshowcitations\showcitationsfalse%
\newif\ifshowlinks\showlinksfalse%

%% CONFIGURATION
%
%% to display citation counts, uncomment the following line
%\showcitationstrue
%
%% to add links to INSPIRE records, uncomment the following line
%\showlinkstrue
%
%% to use the arial font, uncomment the following lines
%\usepackage{arial}
%\renewcommand{\familydefault}{\sfdefault} % Sans serif

\ifshowlinks%
  \usepackage[
         colorlinks=true,
         urlcolor=blue,       % \href{...}{...} external (URL)
         ]{hyperref}
  \newcommand*{\inspireurl}[1]{\\\href{#1}{INSPIRE-HEP entry}}
\else
  \makeatletter
  \newcommand*{\inspireurl}[1]{\@bsphack\@esphack}
  \makeatother
\fi
\ifshowcitations%
  \newcommand*{\citations}[1]{\\* #1}
\else
  \makeatletter
  \newcommand*{\citations}[1]{\@bsphack\@esphack}
  \makeatother
\fi
\renewcommand{\labelenumii}{\arabic{enumi}.\arabic{enumii}}

\pagestyle{empty}
\oddsidemargin 0.0in
\textwidth 6.5in
\topmargin -0.75in
\textheight 9.5in

\begin{document}
\title{}
\author{}
\date{}
\maketitle
\begin{enumerate}

%%%%   LIST OF PAPERS
%%%%   Please send any updates or corrections to the list to
%%%%   admin@inspirehep.net
"""

    POSTAMBLE = r"""
\end{enumerate}
\end{document}"""

    def __init__(self):
        self.style = 'latex_cv'

    def write_preamble(self, bib_data):
        return self.PREAMBLE

    def write_postamble(self, bib_data):
        return self.POSTAMBLE
