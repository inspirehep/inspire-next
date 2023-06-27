from __future__ import absolute_import, division, print_function

import requests_mock
from invenio_workflows import workflow_object_class
from utils import override_config

from inspirehep.modules.literaturesuggest.tasks import reply_ticket_context
from inspirehep.modules.workflows.tasks.submission import (close_ticket,
                                                           create_ticket,
                                                           reply_ticket)
from inspirehep.modules.workflows.utils import \
    _get_headers_for_hep_root_table_request


def test_reply_ticket_calls_tickets_reply_when_template_is_not_set(workflow_app):
    with override_config(FEATURE_FLAG_ENABLE_SNOW=True):
        with requests_mock.Mocker() as request_mocker:
            request_mocker.register_uri(
                "POST",
                "http://web:8000/tickets/reply",
                json={"message": "Ticket was updated with the reply"},
                headers=_get_headers_for_hep_root_table_request(),
                status_code=200,
            )
            data = {
                "titles": [
                    {"title": "Partial Symmetries of Weak Interactions"},
                ],
            }
            extra_data = {"ticket_id": 1, "reason": "reply reason"}
            obj = workflow_object_class.create(
                data=data, extra_data=extra_data, id_user=1, data_type="hep"
            )
            expected_result = {}
            _reply_ticket = reply_ticket()
            result = _reply_ticket(obj, None)
            assert expected_result == result
            assert (
                request_mocker.request_history[0]._request.body
                == '{"ticket_id": "1", "reply_message": "reply reason"}'
            )


def test_reply_ticket_calls_tickets_reply_when_template_is_set(workflow_app):
    with override_config(FEATURE_FLAG_ENABLE_SNOW=True):
        with requests_mock.Mocker() as request_mocker:
            request_mocker.register_uri(
                "POST",
                "http://web:8000/tickets/reply-with-template",
                json={"message": "Ticket was updated with the reply"},
                headers=_get_headers_for_hep_root_table_request(),
                status_code=200,
            )
            data = {
                "titles": [
                    {"title": "Partial Symmetries of Weak Interactions"},
                ],
            }
            extra_data = {"ticket_id": 1}
            obj = workflow_object_class.create(
                data=data, extra_data=extra_data, id_user=1, data_type="hep"
            )
            _reply_ticket = reply_ticket(
                context_factory=reply_ticket_context, template="test.html"
            )
            expected_result = {}
            result = _reply_ticket(obj, None)
            assert expected_result == result
            assert (
                request_mocker.request_history[0]._request.body
                == '{"template_context": {"reason": "", "record_url": "", "user_name": "admin@inspirehep.net", "title": "Partial Symmetries of Weak Interactions"}, "ticket_id": "1", "template": "test"}'
            )


def test_close_ticket_calls_snow_resolve(workflow_app):
    with override_config(FEATURE_FLAG_ENABLE_SNOW=True):
        with requests_mock.Mocker() as request_mocker:
            request_mocker.register_uri(
                "POST",
                "http://web:8000/tickets/resolve",
                json={"message": "Ticket resolved"},
                headers=_get_headers_for_hep_root_table_request(),
                status_code=200,
            )
            data = {
                "titles": [
                    {"title": "Partial Symmetries of Weak Interactions"},
                ],
            }
            extra_data = {"ticket_id": 1, "reason": "reply reason"}
            obj = workflow_object_class.create(
                data=data, extra_data=extra_data, id_user=1, data_type="hep"
            )
            _close_ticket = close_ticket()
            _close_ticket(obj, None)
            assert (
                request_mocker.request_history[0]._request.body == '{"ticket_id": "1", "message": "reply reason"}'
            )


def test_create_ticket_calls_tickets_create_with_template(workflow_app):
    with override_config(FEATURE_FLAG_ENABLE_SNOW=True):
        with requests_mock.Mocker() as request_mocker:
            request_mocker.register_uri(
                "POST",
                "http://web:8000/tickets/create-with-template",
                json={"ticket_id": "123"},
                headers=_get_headers_for_hep_root_table_request(),
                status_code=200,
            )
            data = {
                "titles": [
                    {"title": "Partial Symmetries of Weak Interactions"},
                ],
            }
            template = "template_path"
            extra_data = {"recid": "1"}
            data = {
                "titles": [
                    {"title": "Partial Symmetries of Weak Interactions"},
                ],
            }
            extra_data = {"ticket_id": 1, "reason": "reply reason"}
            obj = workflow_object_class.create(
                data=data, extra_data=extra_data, id_user=1, data_type="hep"
            )
            _create_ticket = create_ticket(template=template, queue="HEP_curation")
            _create_ticket(obj, None)

            assert (
                request_mocker.request_history[0]._request.body
                == '{"functional_category": "arXiv curation", "template_context": {}, "caller_email": "admin@inspirehep.net", "template": "template_path", "subject": "No subject"}'
            )
