# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
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

"""Models for Citations."""

from datetime import datetime

from invenio.ext.sqlalchemy import db


class Citation(db.Model):
    __tablename__ = 'rnkCITATIONDICT'

    citee = db.Column(db.Integer, primary_key=True, index=True)
    citer = db.Column(db.Integer, primary_key=True, index=True)
    last_updated = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __init__(self, citee, citer, last_updated):
        self.citee = citee
        self.citer = citer
        self.last_updated = last_updated

    def save(self):
        db.session.merge(self)


class Citation_Log(db.Model):
    __tablename__ = 'rnkCITATIONLOG'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
        index=True)
    citee = db.Column(db.Integer, nullable=False)
    citer = db.Column(db.Integer, nullable=False)
    action_date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    citation_type = db.Column(
        db.Enum(
            'added',
            'removed',
            name='citation_type'),
        default='added')

    def __init__(self, id, citee, citer, action_date, citation_type):
        self.id = id
        self.citee = citee
        self.citer = citer
        self.action_date = action_date
        self.citation_type = citation_type

    def save(self):
        """ Adds the new log entry to the current session.

            It's also responsible for adding or removing the citation from
            rnkCITATIONDICT table.

        """
        # In case the citation needs to be removed it checks if it already exists
        # and removes it
        if self.citation_type == 'removed':
            cit = Citation.query.filter_by(
                citee=self.citee, citer=self.citer).first()
            if cit is not None:
                db.session.delete(cit)
        # Otherwise it adds the citation at rnkCITATIONDICT table
        else:
            cit = Citation(self.citee, self.citer, self.action_date)
            cit.save()
        # In case the citation alread exists it updates it's data based on the
        # new ones
        db.session.merge(self)
