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

"""Logic of Disambiguation module."""

from __future__ import (
    absolute_import,
    division,
    print_function,
)

from operator import add

import celery
from celery.utils.log import get_task_logger
from flask import current_app

from inspirehep.modules.disambiguation.records import create_author
from inspirehep.modules.disambiguation.search import (
    create_beard_record,
    get_signature,
)

logger = get_task_logger(__name__)


def _check_if_claimed(signature):
    """Check if the signature is claimed.

    In order to proceed with processing the clusters, the signatures
    must be checked if they are claimed by authors.
    However in order to spot a collision (at least two claimed
    signatures from different authors) the method returns a tuple
    representing a claim together with an author profile, to which this
    signature has been assigned.

    :param signature:
        A dictionary representing a signature.

        Example:
            signature = {'author_affiliation': u'MIT, Cambridge, CTP',
                         'author_name': u'Wang, Yi-Nan',
                         'publication_id': u'13c3cca8-b0bf-42f5-90d4-...',
                         'signature_id': u'a4156520-560d-4248-a57f',
                         'author_recid': u'10123',
                         'author_claimed: False}

    :return:
        A tuple representing a claim and an author profile recid.

        Example:
            (False, '1337489')
    """
    return (bool(signature.get('author_claimed', False)),
            str(signature.get('author_recid', None)))


def _create_distance_signature(signatures_map, uuid):
    """Create a signature for a similarity measurement.

    Given a UUID as the parameter, the method
    creates a signature, which will be used to calculate
    the similarity against claimed signatures.

    :param uuid:
        A string representing UUID of a given signature.

        Example:
            uuid = 'd63537a8-1df4-4436-b5ed-224da5b5028c'

    :return:
        Example:
            {u'affiliations': u'Yerevan Phys. Inst.',
             u'publication_id': u'13c3cca8-b0bf-42f5-90d4-e3dfcced0511',
             u'full_name': u'Chatrchyan, Serguei',
             u'uuid': u'd63537a8-1df4-4436-b5ed-224da5b5028c'}

    """
    record = create_beard_record(
        signatures_map[uuid].get('publication_id'))

    beard_signature = signatures_map[uuid].copy()
    beard_signature['publication'] = record

    return beard_signature


def _create_set_from_signature(signature):
    """Create a set based on a given signature.

    The method receives a dictionary representing a signature.
    From a given dictionary it builds a set that will be
    later used in select_profile_base method.

    :param signature:
        A dictionary representing a signature.

        Example:
            signature = {'author_affiliation': u'MIT, Cambridge, CTP',
                         'author_name': u'Wang, Yi-Nan',
                         'publication_id': u'13c3cca8-b0bf-42f5-90d4-...',
                         'signature_id': u'a4156520-560d-4248-a57f',
                         'author_recid': u'10123',
                         'author_claimed: False}

    :return:
        A set of dictionary's values.

        Example:
            {u'MIT, Cambridge, CTP', u'Wang, Yi-Nan'}
    """
    result = set([signature['author_name']])

    if 'author_affiliation' in signature:
        result.update([signature['author_affiliation']])

    return result


def _create_uuid_key_dictionary(signatures):
    """Create a dictionary with UUIDs being used as keys.

    This method creates a dictionary, which keys are exactly
    the same as UUID values of each signatures within the list.
    The value under each key is the signature.
    """
    signatures_dictionary = {}

    for signature in signatures:
        signatures_dictionary[signature['signature_id']] = signature

    return signatures_dictionary


def _select_profile_base(signatures_map, uuids):
    """Select the most rich-in-information signature.

    The method selects a UUID, which signature contains the biggest
    amount of information from the given list of UUIDs, of
    signatures selected to represent the same author.
    Given signatures are converted to sets, then compared against
    each other to calculate the amount of the common values.
    The results are stored in a symmetric matrix, where afterwards
    the shared elements are summed up.
    The signature with the biggest sum is select to be the most
    "representative". In case of the same score, the longest set is
    selected (for example, a signature can have an additional
    affiliation).

    :param signatures_map:
        A dictionary representing signatures with keys
        being exactly the same as the values of UUID of each
        signature.

        Example:
            signatures_map = {u'a4156520-4248-a57f':
                                {'author_affiliation': u'MIT, Cambridge, CTP',
                                 'author_name': u'Wang, Yi-Nan',
                                 'publication_id': u'13c3cca8-b0bf-42f5-90d4-',
                                 'signature_id': u'a4156520-4248-a57f',
                                 'author_recid': u'10123',
                                 'author_claimed': False}
                             }

    :param uuids:
        A list of UUIDs, representing the same author.

        Example:
            uuids = ['6e6e8b99-ee08-43a2-a7c6-136a531a47cc',
                     '4a964f85-762f-4bff-8472-2f47e5f3bb26']

    :return:
        A UUID of a signature selected to be the most representative.

        Example:
            "4a964f85-762f-4bff-8472-2f47e5f3bb26"
    """
    matrix_length = len(uuids)
    matrix = [[0 for x in range(matrix_length)] for y in range(matrix_length)]

    signatures_as_sets = []
    best_results = {}

    for uuid in uuids:
        current_signature = signatures_map[uuid]

        # If a signature is claimed, return it.
        if current_signature['author_claimed']:
            return uuid

        signatures_as_sets.append(
            _create_set_from_signature(current_signature))

    # Since the matrix is symmetric, the method calculates only
    # the values on the right hand side of the diagonal.
    for row in range(len(signatures_as_sets)):
        for column in range(row + 1, len(signatures_as_sets)):
            matrix[row][column] = len(set.intersection(
                signatures_as_sets[row], signatures_as_sets[column]))

    # Make a copy of the values on the right to the left hand side.
    symmetric_matrix = [map(add, i, j) for i, j in zip(
        matrix, map(list, zip(*matrix)))]
    common_elements = [sum(i) for i in symmetric_matrix]

    # If there is only one signature with the highest score, return it.
    if common_elements.count(max(common_elements)) == 1:
        return uuids[common_elements.index(
            max(common_elements))]
    else:
        for result in range(len(common_elements)):
            if common_elements[result] == max(common_elements):
                best_results[uuids[result]] = len(
                    signatures_as_sets[result])

    # Return the signature with the biggest amount of information.
    return max(best_results, key=best_results.get)


def _solve_claims_conflict(signatures_map, not_claimed_uuids,
                           claimed_uuids):
    """Create distance signatures and dispatch task to conflict resolver.

    In case of a conflict, where at least to signatures belonging to two
    different authors, manual resolving must be triggered.

    This method creates signatures in Beard readable format and then
    dispatches a job to Beard Celery instance, to match each not claimed
    signature with a claimed one.

    Check 'process_clusters' for more information.

    :param signatures_map:
        A dictionary representing signatures with keys
        being exactly the same as the values of UUID of each
        signature.

        Example:
            signatures_map = {u'a4156520-4248-a57f':
                                {'author_affiliation': u'MIT, Cambridge, CTP',
                                 'author_name': u'Wang, Yi-Nan',
                                 'publication_id': u'13c3cca8-b0bf-42f5-90d4-',
                                 'signature_id': u'a4156520-4248-a57f',
                                 'author_recid': u'10123',
                                 'author_claimed': False}
                             }

    :param not_claimed_uuids:
        A list of UUIDs, which are not claimed.

        Example:
            uuids = ['4a964f85-762f-4bff-8472-2f47e5f3bb26']

    :param claimed_uuids:
        A list of UUIDs, which are claimed.

        Example:
            uuids = ['6e6e8b99-ee08-43a2-a7c6-136a531a47cc']

    """
    not_claimed_distance_signatures = []
    claimed_distance_signatures = []

    for not_claimed_uuid in not_claimed_uuids:
        not_claimed_distance_signatures.append(
            _create_distance_signature(signatures_map, not_claimed_uuid))

    for claimed_uuid in claimed_uuids:
        claimed_distance_signatures.append(
            _create_distance_signature(signatures_map, claimed_uuid))

    if not_claimed_distance_signatures and claimed_distance_signatures:
        resolved_conflicts = celery.current_app.send_task(
            'beard_server.tasks.solve_conflicts',
            (claimed_distance_signatures,
             not_claimed_distance_signatures),
            queue=current_app.config.get('DISAMBIGUATION_QUEUE'))

        return resolved_conflicts


def process_clusters(uuids, signatures, recid_key=None):
    """Process a given cluster of UUIDs followed by one of provided workflows.

    This method receives a list of UUIDs representing one author, a list
    of signatures and finally recid_key if a cluster was matched with
    already existing cluster of signatures (clustered by the same
    author profile).

    After clustering and matching against existing clusters (if any),
    this method is deciding how the cluster should be processed.

    If the cluster is new (ie. new author, no profile), the method is
    dispatching a job to create a new profile and assigning the given cluster
    to this profile.

    If the cluster was matched with existing cluster (signatures pointing to
    the same author profile), then all signatures will be overwritten to point
    to the profile (recid_key parameter).

    In case if an author has claimed her or his paper (ground truth),
    then it is known that the author has the profile already.
    This profile is overwriting all signatures within the same cluster.

    If the clustering task returned more than two claimed signatures,
    belonging to different authors, then re-clustering is triggered.
    Each of the claimed signatures become a bucket and each not claimed
    one is being allocated to one of the buckets based on the likelihood
    of representing the same author.

    :param uuids:
        A list of signatures, representing the same author.

        Example:
            uuids = ['4156520-560d-4248-a57f-949c361e0dd0']

    :param signatures:
        A list of signatures collected during clustering.

        Example:
            signatures =
                [{'author_affiliation': u'MIT, Cambridge, CTP',
                  'author_name': u'Wang, Yi-Nan',
                  'publication_id': u'9d3dca5d-3551-4ca4-9b52-63db656e4793',
                  'signature_id': u'a4156520-560d-4248-a57f-949c361e0dd0',
                  'author_recid': u'10123',
                  'author_claimed: False}]

    :param recid_key:
        A record id representing profile, which 'old' cluster is
        associated with.

        Example:
            recid_key = '10123'
    """
    from inspirehep.modules.disambiguation.tasks import update_authors_recid

    # Create a map where each signature can be accessed by its uuid.
    signatures_map = _create_uuid_key_dictionary(signatures)

    # Count claimed signatures. Set allows for unique signatures.
    claims = set()

    for uuid in uuids:
        claim_status = _check_if_claimed(signatures_map[uuid])

        # If it is claimed, and profile_id is indeed a digit.
        if claim_status[0] and claim_status[1].isdigit():
            claims.add(claim_status)

    # If there are no claimed signatures and no match with an 'old' cluster.
    if len(claims) == 0 and not recid_key:
        # Select the most rich-in-information signature.
        base_profile = get_signature(_select_profile_base(signatures_map,
                                                          uuids))
        # Create a new profile.
        recid = create_author(base_profile)

        # Update all signatures with the new profile (recid).
        for uuid in uuids:
            record = signatures_map[uuid].get('publication_id')
            update_authors_recid.delay(record, uuid, recid)

        logger.info("A new profile created: %s" % recid)

    # If there are not claimed signatures, but there is a match.
    elif len(claims) == 0 and recid_key:
        # Update all signatures with the profile of the 'old' cluster.
        for uuid in uuids:
            record = signatures_map[uuid].get('publication_id')
            update_authors_recid.delay(record, uuid, recid_key)

    # If there is one claimed signature.
    elif len(claims) == 1:
        # claims format: (False, u'1234')
        recid = claims.pop()[1]

        # Update all signatures with a profile of the claimed signature.
        for uuid in uuids:
            record = signatures_map[uuid].get('publication_id')
            update_authors_recid.delay(record, uuid, recid)

    # If there are more than two claimed signatures,
    # belonging to different authors.
    else:
        claimed_signatures = []
        not_claimed_signatures = []

        # Check each signature if is claimed or not.
        for uuid in uuids:
            claim_status = _check_if_claimed(signatures_map[uuid])

            if not claim_status[0]:
                not_claimed_signatures.append(uuid)

            if claim_status[0]:
                claimed_signatures.append(uuid)

        # Dispatch a resolving conflict job.
        try:
            matched_signatures = _solve_claims_conflict(
                signatures_map,
                not_claimed_signatures,
                claimed_signatures).get()
        except AttributeError:
            matched_signatures = {}

        # For each claimed signature, assign recid of it to not claimed ones.
        for claimed_uuid, uuids in matched_signatures.items():
            recid = signatures_map[claimed_uuid].get('author_recid')

            for uuid in uuids:
                record = signatures_map[uuid].get('publication_id')
                update_authors_recid.delay(record, uuid, recid)
