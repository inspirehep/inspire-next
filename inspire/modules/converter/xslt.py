# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2014, 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""
bibconvert_xslt_engine - Wrapper for an XSLT engine.

Customized to support BibConvert functions through the
use of XPath 'format' function.

Used by: bibconvert.in

FIXME: - Find better namespace for functions
       - Find less bogus URI (given as param to processor)
         for source and template
       - Implement command-line options
       - Think about better handling of 'value' parameter
         in bibconvert_function_*
"""

from __future__ import print_function

import os
import sys
import string
from StringIO import StringIO

from lxml import etree
from invenio.utils.text import encode_for_xml

from .registry import templates, kb

CFG_BIBCONVERT_FUNCTION_NS = "http://cdsweb.cern.ch/bibconvert/fn"
"""The namespace used for BibConvert functions"""


def crawl_KB(filename, value, mode):
    """
    bibconvert look-up value in KB_file in one of following modes:
    ===========================================================
    1                           - case sensitive     / match  (default)
    2                           - not case sensitive / search
    3                           - case sensitive     / search
    4                           - not case sensitive / match
    5                           - case sensitive     / search (in KB)
    6                           - not case sensitive / search (in KB)
    7                           - case sensitive     / search (reciprocal)
    8                           - not case sensitive / search (reciprocal)
    9                           - replace by _DEFAULT_ only
    R                           - not case sensitive / search (reciprocal) (8) replace
    """

    if (os.path.isfile(filename) != 1):
        # Look for KB in same folder as extract_tpl, if exists
        try:
            pathtmp = string.split(extract_tpl,"/")
            pathtmp.pop()
            path = string.join(pathtmp,"/")
            filename = path + "/" + filename
        except NameError:
            # File was not found. Try to look inside default KB
            # directory
            filename = kb.get(filename, '')

    # FIXME: Remove \n from returned value?
    if (os.path.isfile(filename)):

        file_to_read = open(filename,"r")

        file_read = file_to_read.readlines()
        for line in file_read:
            code = string.split(line, "---")

            if (mode == "2"):
                value_to_cmp   = string.lower(value)
                code[0]        = string.lower(code[0])

                if ((len(string.split(value_to_cmp, code[0])) > 1) \
                    or (code[0]=="_DEFAULT_")):
                    value = code[1]
                    return value

            elif ((mode == "3") or (mode == "0")):
                if ((len(string.split(value, code[0])) > 1) or \
                    (code[0] == "_DEFAULT_")):
                    value = code[1]
                    return value

            elif (mode == "4"):
                value_to_cmp   = string.lower(value)
                code[0]        = string.lower(code[0])
                if ((code[0] == value_to_cmp) or \
                    (code[0] == "_DEFAULT_")):
                    value = code[1]
                    return value

            elif (mode == "5"):
                if ((len(string.split(code[0], value)) > 1) or \
                    (code[0] == "_DEFAULT_")):
                    value = code[1]
                    return value

            elif (mode == "6"):
                value_to_cmp   = string.lower(value)
                code[0]        = string.lower(code[0])
                if ((len(string.split(code[0], value_to_cmp)) > 1) or \
                    (code[0] == "_DEFAULT_")):
                    value = code[1]
                    return value

            elif (mode == "7"):
                if ((len(string.split(code[0], value)) > 1) or \
                    (len(string.split(value,code[0])) > 1) or \
                    (code[0] == "_DEFAULT_")):
                    value = code[1]
                    return value

            elif (mode == "8"):
                value_to_cmp   = string.lower(value)
                code[0]        = string.lower(code[0])
                if ((len(string.split(code[0], value_to_cmp)) > 1) or \
                    (len(string.split(value_to_cmp, code[0])) > 1) or \
                    (code[0] == "_DEFAULT_")):
                    value = code[1]
                    return value

            elif (mode == "9"):
                if (code[0]=="_DEFAULT_"):
                    value = code[1]
                    return value

            elif (mode == "R"):
                value_to_cmp   = string.lower(value)
                code[0]        = string.lower(code[0])
                if ((len(string.split(code[0], value_to_cmp)) > 1) or \
                    (len(string.split(value_to_cmp, code[0])) > 1) or \
                    (code[0] == "_DEFAULT_")):
                    value = value.replace(code[0], code[1])

            else:
                if ((code[0] == value) or (code[0]=="_DEFAULT_")):
                    value = code[1]
                    return value
    else:
        sys.stderr.write("Warning: given KB could not be found. \n")

    return value


def get_pars(fn):
    "Read function and its parameters into list"

    out = []

    out.append(re.split('\(|\)', fn)[0])
    out.append(re.split(',', re.split('\(|\)', fn)[1]))

    return out

def sub_keywd(out):
    "bibconvert keywords literal substitution"


    out = string.replace(out, "EOL", "\n")
    out = string.replace(out, "_CR_", "\r")
    out = string.replace(out, "_LF_", "\n")
    out = string.replace(out, "\\", '\\')
    out = string.replace(out, "\r", '\r')
    out = string.replace(out, "BSLASH", '\\')
    out = string.replace(out, "COMMA", ',')
    out = string.replace(out, "LEFTB", '[')
    out = string.replace(out, "RIGHTB", ']')
    out = string.replace(out, "LEFTP", '(')
    out = string.replace(out, "RIGHTP", ')')

    return out


def set_par_defaults(par1, par2):
    "Set default parameter when not defined"

    par_new_in_list = par2.split(",")
    i = 0
    out = []
    for par in par_new_in_list:

        if (len(par1) > i):
            if (par1[i] == ""):
                out.append(par)
            else:
                out.append(par1[i])
        else:
            out.append(par)
        i = i + 1

    return out


def FormatField(value, fn):
    """PLEASE KILL ME."""

    global data_parsed

    out     = value
    fn      = fn + "()"
    par     = get_pars(fn)[1]
    fn      = get_pars(fn)[0]
    regexp  = "//"
    NRE     = len(regexp)
    value   = sub_keywd(value)
    par_tmp = []

    for item in par:
        item = sub_keywd(item)
        par_tmp.append(item)
    par = par_tmp

    if (fn == "KB"):
        new_value = ""

        par = set_par_defaults(par, "KB,0")

        new_value = crawl_KB(par[0], value, par[1])

        out = new_value

    return out


class FileResolver(etree.Resolver):

    """Local file resolver."""

    def resolve(self, url, pubid, context):
        """Resolve local name."""
        return self.resolve_filename(url, context)


def _bibconvert_escape(dummy_ctx, value):
    """Bridge to lxml to escape the provided value."""
    try:
        if isinstance(value, str):
            string_value = value
        elif isinstance(value, (int, long)):
            string_value = str(value)
        elif isinstance(value, list):
            value = value[0]
            if isinstance(value, str):
                string_value = value
            elif isinstance(value, (int, long)):
                string_value = str(value)
            else:
                string_value = value.text
        else:
            string_value = value.text

        return encode_for_xml(string_value)

    except Exception as err:
        print("Error during formatting function evaluation: {0}".format(err),
              file=sys.stderr)

    return ''


def _bibconvert_function(dummy_ctx, value, func):
    """
    Bridge between BibConvert formatting functions and XSL stylesheets.

    Can be used in that way in XSL stylesheet (provided
    ``xmlns:fn="http://cdsweb.cern.ch/bibconvert/fn"`` has been declared):
    ``<xsl:value-of select="fn:format(., 'ADD(mypref,mysuff)')"/>``
    (Adds strings ``mypref`` and ``mysuff`` as prefix/suffix to current node
    value, using BibConvert ADD function)

    if value is int, value is converted to string
    if value is Node (PyCObj), first child node (text node) is taken as value

    """
    try:
        if isinstance(value, str):
            string_value = value
        elif isinstance(value, (int, long)):
            string_value = str(value)
        elif isinstance(value, list):
            value = value[0]
            if isinstance(value, str):
                string_value = value
            elif isinstance(value, (int, long)):
                string_value = str(value)
            else:
                string_value = value.text
        else:
            string_value = value.text

        return FormatField(string_value, func).rstrip('\n')

    except Exception as err:
        print("Error during formatting function evaluation: {0}".format(err),
              file=sys.stderr)

    return ''


def convert(xmltext, template_filename=None, template_source=None):
    """
    Process an XML text according to a template, and returns the result.

    The template can be given either by name (or by path) or by source.
    If source is given, name is ignored.

    bibconvert_xslt_engine will look for template_filename in standard
    directories for templates. If not found, template_filename will be assumed
    to be a path to a template. If none can be found, return None.

    :param xmltext: The string representation of the XML to process
    :param template_filename: The name of the template to use for the processing
    :param template_source: The configuration describing the processing.
    :return: the transformed XML text, or None if an error occured

    """
    # Retrieve template and read it
    if template_source:
        template = template_source
    elif template_filename:
        try:
            path_to_templates = templates.get(template_filename, '')
            if os.path.exists(path_to_templates):
                template = file(path_to_templates).read()
            elif os.path.exists(template_filename):
                template = file(template_filename).read()
            else:
                raise Exception(template_filename + ' does not exist.')
        except IOError:
            raise Exception(template_filename + ' could not be read.')
    else:
        raise Exception(template_filename + ' was not given.')

    result = ""

    parser = etree.XMLParser()
    parser.resolvers.add(FileResolver())
    try:
        try:
            if (-1 < xmltext.index('?') < 3):
                xmltext = xmltext[xmltext.index('>') + 1:]
        except ValueError:
            # if index doesn't find the '?' then it raises a useless exception
            pass

        xml = etree.parse(StringIO(xmltext), parser)
    except etree.XMLSyntaxError as e:
        error = 'The XML code given is invalid. [%s]' % e
        raise Exception(error)
    except Exception as e:
        error = 'Failed to process the XML code.' + str(e)
        raise Exception(error)

    try:
        xsl = etree.parse(StringIO(template), parser)
    except etree.XMLSyntaxError as e:
        error = 'The XSL code given is invalid. [%s]' % e
        raise Exception(error)
    except Exception as e:
        error = 'Failed to process the XSL code.' + str(e)
        raise Exception(error)

    try:
        fns = etree.FunctionNamespace(CFG_BIBCONVERT_FUNCTION_NS)
        fns["escape"] = _bibconvert_escape
        fns["format"] = _bibconvert_function
    except etree.NamespaceRegistryError as e:
        error = 'Failed registering the XPath extension function. [%s]' % e
        raise Exception(error)

    try:
        xslt = etree.XSLT(xsl)
    except etree.XSLTParseError as e:
        error = 'The XSL code given is invalid. [%s]' % e
        raise Exception(error)

    temporary_result = xslt(xml)
    result = str(temporary_result)

    # Housekeeping
    del temporary_result
    del xslt
    del xsl
    del xml

    return result
