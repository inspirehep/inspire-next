"""
DELETE UNUSABLE ORCID TOKENS.

ORCID tokens are encrypted using an env-specific key.
Thus copying tokens from PROD db to QA db might result in unusable tokens.
This snippet can be used to delete those unusable tokens.
"""

import re

from invenio_db import db
from invenio_oauthclient.models import RemoteToken


def find_unusable_orcid_tokens():
    # Access tokens are in the form:
    #   "7559f1gt-a65g-49s4-9cf4-35b27989289f"
    # Unusable access tokens are in the form:
    #   "s\x1b\xf6\xf4\xd0B\xe1j\x82\x918IM\xfc{\xe6\xb8\x1d}g\xc6\xac\xd0'\xe1+\xcbh\xb3\x1em\xaa'\x0c\xaf3t\xbd\xb3\x915\x80\xf8Pqh(H"
    compiled = re.compile(r'^[\w\-]*$')
    for remote_token in RemoteToken.query.all():
        if not re.match(compiled, remote_token.access_token):
            yield remote_token


def delete_unusable_orcid_tokens():
    for token in find_unusable_orcid_tokens():
        print 'Deleting token with extra data: ', token.remote_account.extra_data
        db.session.delete(token)
        db.session.delete(token.remote_account)
        db.session.commit()
