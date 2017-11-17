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

"""Add record metadata indices."""

from __future__ import absolute_import, division, print_function

from alembic import op

# revision identifiers, used by Alembic.
revision = 'cb9f81e8251c'
down_revision = 'fddb3cfe7a9c'
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.execute(
        "CREATE INDEX idxgindoctype ON records_metadata USING gin ((json -> 'document_type'))"
    )
    op.execute(
        "CREATE INDEX idxgintitles ON records_metadata USING gin ((json -> 'titles'))"
    )
    op.execute(
        "CREATE INDEX idxginjournaltitle ON records_metadata USING gin ((json -> 'journal_title'))"
    )
    op.execute(
        "CREATE INDEX idxgincollections ON records_metadata USING gin ((json -> '_collections'))"
    )


def downgrade():
    """Downgrade database."""
    op.execute("DROP INDEX IF EXISTS idxgindoctype")
    op.execute("DROP INDEX IF EXISTS idxgintitles")
    op.execute("DROP INDEX IF EXISTS idxginjournaltitle")
    op.execute("DROP INDEX IF EXISTS idxgincollections")
