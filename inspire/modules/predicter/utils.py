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

"""Utilities for classifier."""

from cPickle import load


def get_classification_from_task_results(obj):
    """Return the classification output from a object's task results."""
    tasks_results = obj.get_tasks_results()
    if "classification" in tasks_results:
        classification = tasks_results.get("classification")[0]
    elif "classification_full" in tasks_results:
        classification = tasks_results.get("classification_full")[0]
    elif "classification_fast" in tasks_results:
        classification = tasks_results.get("classification_fast")[0]
    else:
        obj.log.info("No classification results found.")
        return
    try:
        return classification.get("result").get("dict").get("complete_output")
    except AttributeError:
        obj.log.info("Problem getting classification from {0}.".format(
            classification
        ))
        return


def update_classification_in_task_results(obj, output):
    """Return the classification output from a object's task results."""
    tasks_results = obj.get_tasks_results()
    name = ""
    if "classification" in tasks_results:
        classification = tasks_results.get("classification")[0]
        name = "classification"
    elif "classification_full" in tasks_results:
        classification = tasks_results.get("classification_full")[0]
        name = "classification_full"
    elif "classification_fast" in tasks_results:
        classification = tasks_results.get("classification_fast")[0]
        name = "classification_fast"
    else:
        obj.log.info("No classification results found.")
        return
    try:
        classification["result"]["dict"]["complete_output"] = output
        obj.update_task_results(name, [classification])
    except AttributeError:
        obj.log.info("Problem getting classification from {0}.".format(
            classification
        ))
        return


def prepare_prediction_record(metadata):
    """Given a workflow object, return compatible prediction record."""
    prepared_record = {}
    prepared_record["title"] = ". ".join(metadata.get("title.title", []))
    abstract = metadata.get("abstract.summary")
    if abstract:
        prepared_record["abstract"] = abstract[0]
    else:
        prepared_record["abstract"] = ""
    categories = []
    for category in metadata.get("subject_term"):
        if category.get("scheme").lower() == "arxiv":
            categories.append(category.get("term", ""))
    prepared_record["categories"] = categories
    return prepared_record


def load_model(path_to_object):
    """Load a pickled prediction model."""
    return load(open(path_to_object))
