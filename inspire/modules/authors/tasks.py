#
## This file is part of INSPIRE.
## Copyright (C) 2015 CERN.
##
## INSPIRE is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#

import os


from datetime import date
from functools import wraps
from flask import render_template

from invenio.modules.access.control import acc_get_user_email

from inspire.modules.deposit.utils import filter_empty_helper
from inspire.modules.workflows.tasks.submission import submit_rt_ticket


def filter_empty_elements(recjson):
    """Filter empty fields."""
    list_fields = [
        'institution_history', 'advisors', 'websites', 'experiments'
    ]
    for key in list_fields:
        recjson[key] = filter(
            filter_empty_helper(), recjson.get(key, [])
        )

    for k in recjson.keys():
        if not recjson[k]:
            del recjson[k]

    return recjson


def create_marcxml_record():
    """Create MarcXML from JSON using author model."""
    @wraps(create_marcxml_record)
    def _create_marcxml_record(obj, eng):
        from invenio_records.api import Record
        obj.log.info("Creating marcxml record")
        x = Record.create(obj.data, 'json', model='author')
        obj.extra_data["marcxml"] = x.legacy_export_as_marc()
        obj.log.info("Produced MarcXML: \n {}".format(
            obj.extra_data["marcxml"])
        )
    return _create_marcxml_record


def convert_data_to_model():
    """Manipulate form data to match author model keys."""
    @wraps(create_marcxml_record)
    def _convert_data_to_model(obj, eng):
        import copy
        # Save original form data for later access
        obj.extra_data["formdata"] = copy.deepcopy(obj.data)

        data = obj.data
        filter_empty_elements(data)

        data["name"] = {}
        if "status" in data and data["status"]:
            data["name"]["status"] = data["status"]
        if "given_names" in data and data["given_names"]:
            data["name"]["first"] = data["given_names"].strip()
        if "family_name" in data and data["family_name"]:
            data["name"]["last"] = data["family_name"].strip()
        if "display_name" in data and data["display_name"]:
            data["name"]["preferred_name"] = data["display_name"]
        data["urls"] = []
        if "websites" in data and data["websites"]:
            for website in data["websites"]:
                data["urls"].append({
                    "value": website["webpage"],
                    "description": ""
                })
        if "twitter_url" in data and data["twitter_url"]:
            data["urls"].append({
                "value": data["twitter_url"],
                "description": "TWITTER"
            })
        if "blog_url" in data and data["blog_url"]:
            data["urls"].append({
                "value": data["blog_url"],
                "description": "BLOG"
            })
        if "linkedin_url" in data and data["linkedin_url"]:
            data["urls"].append({
                "value": data["linkedin_url"],
                "description": "LINKEDIN"
            })
        data["ids"] = []
        if "orcid" in data and data["orcid"]:
            data["ids"].append({
                "type": "ORCID",
                "value": data["orcid"]
            })
        if "bai" in data and data["bai"]:
            data["ids"].append({
                "type": "BAI",
                "value": data["bai"]
            })
        if "inspireid" in data and data["inspireid"]:
            data["ids"].append({
                "type": "INSPIRE",
                "value": data["inspireid"]
            })
        data["_public_emails"] = []
        if "public_email" in data and data["public_email"]:
            data["_public_emails"].append({
                "value": data["public_email"],
                "current": "Current"
            })
        data["field_categories"] = []
        if "research_field" in data and data["research_field"]:
            for field in data["research_field"]:
                data["field_categories"].append({
                    "name": field,
                    "type": "INSPIRE"
                })
            del data["research_field"]
        data["positions"] = []
        if "institution_history" in data and data["institution_history"]:
            data["institution_history"] = sorted(data["institution_history"],
                                                 key=lambda k: k["start_year"],
                                                 reverse=True)
            for position in data["institution_history"]:
                data["positions"].append({
                    "institution": position["name"],
                    "status": "current" if position["current"] else "",
                    "start_date": position["start_year"],
                    "end_date": position["end_year"],
                    "rank": position["rank"] if position["rank"] != "rank" else ""
                })
            del data["institution_history"]
        data["phd_advisors"] = []
        if "advisors" in data and data["advisors"]:
            for advisor in data["advisors"]:
                if advisor["degree_type"] == "PhD" and not advisor["full_name"]:
                    continue
                data["phd_advisors"].append({
                    "name": advisor["full_name"],
                    "degree_type": advisor["degree_type"]
                })
        if "experiments" in data and data["experiments"]:
            for experiment in data["experiments"]:
                data["experiments"] = sorted(data["experiments"],
                                             key=lambda k: k["start_year"],
                                             reverse=True)
                if experiment["status"]:
                    experiment["status"] = "current"
                else:
                    experiment["status"] = ""

        # Add comments to extra data
        if "comments" in data and data["comments"]:
            obj.extra_data["comments"] = data["comments"]
            data["_private_note"] = data["comments"]

        # Add HEPNAMES collection
        data["collections"] = {
            "primary": "HEPNAMES"
        }

        # ==========
        # Owner Info
        # ==========
        user_email = acc_get_user_email(obj.id_user)
        sources = ["{0}{1}".format('inspire:uid:', obj.id_user)]
        data['acquisition_source'] = dict(
            source=sources,
            email=user_email,
            date=date.today().isoformat(),
            method="submission",
            submission_number=obj.id,
        )

    return _convert_data_to_model


def send_robotupload(mode="insert"):
    """Gets the MARCXML from the workflow object and ships it."""
    @wraps(send_robotupload)
    def _send_robotupload(obj, eng):
        from invenio.base.globals import cfg
        from invenio.modules.workflows.errors import WorkflowError
        from inspire.utils.robotupload import make_robotupload_marcxml

        callback_url = os.path.join(cfg["CFG_SITE_URL"],
                                    "callback/workflows/robotupload")

        marcxml = obj.get_extra_data().get("marcxml")

        if not marcxml:
            obj.log.error("No MARCXML found in extra data.")

        result = make_robotupload_marcxml(
            url=None,
            marcxml=marcxml,
            callback_url=callback_url,
            mode=mode,
            nonce=obj.id
        )
        if "[INFO]" not in result.text:
            if "cannot use the service" in result.text:
                # IP not in the list
                obj.log.error("Your IP is not in "
                              "CFG_BATCHUPLOADER_WEB_ROBOT_RIGHTS "
                              "on host")
                obj.log.error(result.text)
            txt = "Error while submitting robotupload: {0}".format(result.text)
            raise WorkflowError(txt, eng.uuid, obj.id)
        else:
            obj.log.info("Robotupload sent!")
            obj.log.info(result.text)
            if mode != "holdingpen":
                eng.halt("Waiting for robotupload: {0}".format(result.text))
        obj.log.info("end of upload")

    return _send_robotupload


def create_curator_ticket_update(template, queue="Test",
                                 ticket_id_key="ticket_id"):
    """Create a curation ticket for updates.

    This ticket is created when a user updates an author. The user
    will not be notified at this stage. Only when a reply is done to
    this ticket the user will receive an email.
    """

    @wraps(create_curator_ticket_update)
    def _create_curator_ticket_update(obj, eng):
        from invenio.base.globals import cfg

        user_email = acc_get_user_email(obj.id_user)
        recid = obj.data.get("recid", "")

        subject = "Your update to author {} on INSPIRE".format(
            obj.data.get("name").get("preferred_name")
        )
        record_url = os.path.join(cfg["AUTHORS_UPDATE_BASE_URL"], "record",
                                  str(recid))
        body = render_template(
            template,
            email=user_email,
            url=record_url,
            bibedit_url=record_url + "/edit",
            user_comment=obj.extra_data.get("comments", ""),
        ).strip()

        submit_rt_ticket(
            obj=obj,
            queue=queue,
            subject=subject,
            body=body,
            requestors=user_email,
            ticket_id_key=ticket_id_key
        )
    return _create_curator_ticket_update


def create_curator_ticket_new(template, queue="Test",
                              ticket_id_key="ticket_id"):
    """Create a curation ticket for new authors.

    This ticket is created when a user creates a new author. The user
    will not be notified at this stage. Only when a reply is done to
    this ticket the user will receive an email.
    """

    @wraps(create_curator_ticket_new)
    def _create_curator_ticket_new(obj, eng):
        user_email = acc_get_user_email(obj.id_user)

        subject = "Your suggestion to INSPIRE: author {}".format(
            obj.data.get("name").get("preferred_name")
        )
        body = render_template(
            template,
            email=user_email,
            object=obj,
            user_comment=obj.extra_data.get("comments", ""),
        ).strip()

        submit_rt_ticket(
            obj=obj,
            queue=queue,
            subject=subject,
            body=body,
            requestors=user_email,
            ticket_id_key=ticket_id_key
        )
    return _create_curator_ticket_new


def reply_ticket(template=None, keep_new=False):
    """Reply to a ticket for the submission."""
    @wraps(reply_ticket)
    def _reply_ticket(obj, eng):
        from invenio.modules.accounts.models import User
        from invenio.modules.workflows.errors import WorkflowError
        from inspire.utils.tickets import get_instance
        from flask import render_template

        ticket_id = obj.extra_data.get("ticket_id", "")
        if not ticket_id:
            obj.log.error("No ticket ID found!")
            return

        if template:
            # Body rendered by template.
            user = User.query.get(obj.id_user)

            context = {
                "object": obj,
                "user": user,
                "author_name": obj.data.get("name").get("preferred_name"),
                "reason": obj.extra_data.get("reason", ""),
                "record_url": obj.extra_data.get("url", ""),
            }

            body = render_template(
                template,
                **context
            )
        else:
            # Body already rendered in reason.
            body = obj.extra_data.get("reason").strip()
        if not body:
            raise WorkflowError("No body for ticket reply")
        # Trick to prepare ticket body
        body = "\n ".join([line.strip() for line in body.strip().split("\n")])

        rt = get_instance()
        if not rt:
            obj.log.error("No RT instance available. Skipping!")
        else:
            rt.reply(
                ticket_id=ticket_id,
                text=body,
            )
            obj.log.info("Reply created:\n{0}".format(
                body.encode("utf-8", "ignore")
            ))
            if keep_new:
                # We keep the state as new
                rt.edit_ticket(
                    ticket_id=ticket_id,
                    Status="new"
                )
    return _reply_ticket


def curation_ticket_needed(obj, eng):
    """Check if the a curation ticket is needed."""
    extra_data = obj.get_extra_data()
    return extra_data.get("ticket", False)


def create_curation_ticket(template, queue="Test", ticket_id_key="ticket_id"):
    """Create a ticket for author curation.

    Creates the ticket in the given queue and stores the ticket ID
    in the extra_data key specified in ticket_id_key."""
    @wraps(create_curation_ticket)
    def _create_curation_ticket(obj, eng):
        from invenio.modules.access.control import acc_get_user_email

        recid = obj.extra_data.get('recid')
        record_url = obj.extra_data.get('url')

        user_email = acc_get_user_email(obj.id_user)

        bai = ""
        if obj.data.get("bai"):
            bai = "[{}]".format(obj.data.get("bai"))
        subject = "Curation needed for author {} {}".format(
            obj.data.get("name").get("preferred_name"),
            bai
        )
        body = render_template(
            template,
            email=user_email,
            object=obj,
            recid=recid,
            record_url=record_url,
            user_comment=obj.extra_data.get("comments", ""),
        ).strip()

        submit_rt_ticket(
            obj=obj,
            queue=queue,
            subject=subject,
            body=body,
            requestors=user_email,
            ticket_id_key=ticket_id_key
        )

    return _create_curation_ticket
