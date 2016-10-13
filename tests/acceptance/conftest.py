# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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

"""Pytest configuration for web tests."""

from __future__ import absolute_import, division, print_function

from os import environ
from time import sleep

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from invenio_db import db
from invenio_search import current_search_client as es

from inspirehep.config import SERVER_NAME
from inspirehep.factory import create_app


@pytest.fixture(scope='session')
def app(request):
    """Flask application fixture."""
    app = create_app()
    app.config.update({'DEBUG': True})

    with app.app_context():
        # Imports must be local, otherwise tasks default to pickle serializer.
        from inspirehep.modules.migrator.tasks.records import migrate
        from inspirehep.modules.fixtures.collections import init_collections
        from inspirehep.modules.fixtures.files import init_all_storage_paths
        from inspirehep.modules.fixtures.users import init_users_and_permissions

        db.drop_all()
        db.create_all()

        sleep(10)
        _es = app.extensions['invenio-search']
        list(_es.delete(ignore=[404]))
        list(_es.create(ignore=[400]))

        init_all_storage_paths()
        init_users_and_permissions()
        init_collections()

        migrate('./inspirehep/demosite/data/demo-records-acceptance.xml', wait_for_results=True)
        es.indices.refresh('records-hep')

        yield app


@pytest.fixture
def selenium(selenium, app):
    selenium.implicitly_wait(10)
    selenium.maximize_window()
    selenium.get(environ['SERVER_NAME'])
    return selenium


@pytest.fixture
def login(selenium):
    selenium.find_element_by_link_text('Sign in').click()
    selenium.get(environ['SERVER_NAME'] + '/login/?local=1')
    selenium.find_element_by_id('email').send_keys('admin@inspirehep.net')
    selenium.find_element_by_id('password').send_keys('123456')
    selenium.find_element_by_xpath("//button[@type='submit']").click()

    yield

    selenium.execute_script('document.getElementById("toast-container").style.display = "none"')
    WebDriverWait(selenium, 10).until(EC.visibility_of_element_located((By.ID, 'user-info')))
    selenium.find_element_by_id("user-info").click()
    selenium.find_element_by_xpath("(//button[@type='button'])[2]").click()
