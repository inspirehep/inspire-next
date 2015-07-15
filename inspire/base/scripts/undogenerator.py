# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

""" Parse dojson rules and generate rules to undo. """

import glob
import pkg_resources
import os
import re


HEP_REGEXP = re.compile(r"@(?P<model>\w+)\..*['\"](?P<key>\w+)['\"].*['\"](?P<tag>.+)['\"]")
DICT_REGEXP = re.compile(r"\s*'(?P<key>.+)':\s.*'(?P<value>.+)'\s*")
DEF_REGEXP = re.compile(r"def (\w+)\s*\((.*?)\):")


filenames = [
            pkg_resources.resource_filename("inspire.dojson", x) for
            x in pkg_resources.resource_listdir("inspire", "dojson")
            ]
dirs = [filename for filename in filenames if os.path.isdir(filename)]

for dir in dirs:
    dirname = dir.split("/")[-1]
    outfilename = pkg_resources.resource_filename("inspire", "dojson") + "/" + dirname + ".py"
    outfile = open(outfilename, "a")
    fieldfiles = glob.glob(dir + "/fields/bd*.py")
    for fieldfile in fieldfiles:
        infile = open(fieldfile)
        loop = False
        space = 0
        for line in infile.readlines():
            hep_regex = HEP_REGEXP.match(line)
            dict_regex = DICT_REGEXP.match(line)
            def_regex = DEF_REGEXP.match(line)
            if hep_regex:
                model, key, tag = hep_regex.groups()
                outfile.write("@{}.over('{}', '{}')\n".format(
                    model + "2marc",
                    tag,
                    key))
            elif dict_regex:
                key, value = dict_regex.groups()
                outfile.write("{}'{}': value.get('{}'),\n".format(
                    " " * 8,
                    value,
                    key))
            elif def_regex:
                name = def_regex.groups()[0]
                outfile.write("def {}(self, key, value):\n".format(
                    name + "2marc"))
            else:
                outfile.write(line)

        infile.close()
    outfile.close()
