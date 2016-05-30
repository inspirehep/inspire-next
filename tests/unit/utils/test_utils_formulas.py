# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Test formulas utils."""


from inspirehep.utils import formulas


def test_whole_formula_extraction():
    """Test simple formulas."""
    text = ur"""Study of the $B_c^+ \to J/\psi D_s^+$ and $B_c^+ \to J/\psi D_s^{*+}$ decays with the ATLAS detector"""
    tokens = {
        u'Bc+',
        u'Bc+→J/ψDs+',
        u'ψDs∗+',
        u'J/ψDs+',
        u'J',
        u'Bc+→J/ψDs∗+',
        u'J/ψDs∗+',
        u'ψDs+'}
    assert formulas.get_all_unicode_formula_tokens_from_text(text) == tokens


def test_sqrt():
    """Test with sqrt."""
    text = ur"$\sqrt{2.3}$"
    tokens = {
        u'2.3',
        u'√(2.3)'}
    assert formulas.get_all_unicode_formula_tokens_from_text(text, only_decays=False) == tokens


def test_parentheses():
    """Test formula with parentheses."""
    text = ur"Measurement of the ratio of branching fractions $\mathcal{B}(\bar{B}^0 \to D^{*+}\tau^{-}\bar{\nu}_{\tau})/\mathcal{B}(\bar{B}^0 \to D^{*+}\mu^{-}\bar{\nu}_{\mu})$"
    tokens = {
        u'D∗+τ−ν¯τ',
        u'D∗+μ−ν¯μ',
        u'B(B¯0→D∗+τ−ν¯τ)/B(B¯0→D∗+μ−ν¯μ)',
        u'B¯0→D∗+τ−ν¯τ',
        u'B¯0',
        u'B¯0→D∗+μ−ν¯μ'}
    assert formulas.get_all_unicode_formula_tokens_from_text(text) == tokens


def test_equals():
    """Test formula with equals."""
    text = ur"$\sqrt{s_{NN}}=5~\mathrm{TeV}$"
    tokens = {
        u'sNN',
        u'5 TeV',
        u'√(sNN)',
        u'√(sNN)=5 TeV'}
    assert formulas.get_all_unicode_formula_tokens_from_text(text, only_decays=False) == tokens
