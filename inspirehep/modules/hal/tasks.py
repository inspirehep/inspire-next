# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2018 CERN.
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

"""HAL tasks."""

from __future__ import absolute_import, division, print_function

import datetime
import os
import socket

import smtplib
from celery import shared_task
from celery.utils.log import get_task_logger
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from inspirehep.modules.hal.bulk_push import HAL_LOG_FILE, run


logger = get_task_logger(__name__)


@shared_task(ignore_result=True)
def hal_push(username, password, limit, yield_amt, mailing_list=None):
    """Run a hal push.
    """
    logger.info('HAL: Starting to process HAL records')
    if mailing_list:
        send_hal_push_start_email(mailing_list)

    total, now, ok, ko = run(
        username=username,
        password=password,
        limit=limit,
        yield_amt=yield_amt,
    )

    logger.info(
        'HAL: Finished, %s records processed in %s: %s ok, %s ko'
        % (total, now, ok, ko)
    )
    if mailing_list:
        send_hal_push_summary_email(
            mailing_list=mailing_list,
            total=total,
            ok=ok,
            now=now,
            ko=ko,
            attached_files=[HAL_LOG_FILE],
        )


def send_hal_push_start_email(mailing_list):
    host = socket.gethostname()
    body = '''
Hi!!

Hal push just started to run in host %s, you should receive an email once it's
finished too with the logs.

Cheers!
The Inspire developers team
    ''' % (host)
    message = MIMEText(body)
    timestamp = datetime.datetime.now().strftime('[%Y/%m/%d-%H:%M:%S]')
    message['Subject'] = 'Hal push starting at %s' % timestamp
    message['From'] = 'inspire-halpush@cern.ch'
    message['To'] = mailing_list

    cli = smtplib.SMTP('localhost')
    try:
        cli.sendmail(
            from_addr=message['From'],
            to_addrs=[message['To']],
            msg=message.as_string(),
        )
    finally:
        cli.close()


def send_hal_push_summary_email(mailing_list, total, ok, now, ko, attached_files=None):
    """Sends a nice email with the summary of the hal push.
    """
    body = MIMEText('''
The hal push has finished!

We processed %s records in %s: %s ok, %s ko.

There's (or should be) some logs attached to this email.


Enjoy!
    ''' % (total, now, ok, ko))
    body.add_header('Content-type', 'text/plain')

    message = MIMEMultipart()
    timestamp = datetime.datetime.now().strftime('[%Y/%m/%d-%H:%M:%S]')
    message['Subject'] = 'Hal push finished at %s' % timestamp
    message['From'] = 'inspire-halpush@cern.ch'
    message['To'] = mailing_list

    message.attach(body)

    cli = smtplib.SMTP('localhost')

    for file_name in attached_files:
        if not os.path.exists(file_name):
            logger.warning(
                'HAL: Unable to find file %s to attach to deploy end email.' %
                file_name
            )
            continue

        with open(file_name, 'rb') as file_fd:
            attached_file = MIMEText(file_fd.read())

        attached_file.add_header(
            'Content-Disposition',
            'attached',
            filename=file_name,
        )
        message.attach(attached_file)

    try:
        cli.sendmail(
            from_addr=message['From'],
            to_addrs=[message['To']],
            msg=message.as_string(),
        )
    finally:
        cli.close()
