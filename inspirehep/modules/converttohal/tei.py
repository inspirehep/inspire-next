#!/usr/bin/python

from jinja2 import Environment, PackageLoader
import json

TEMPLATE = 'default.xml'
#from inspirehep.utils.record_getter import get_es_record
from inspirehep.modules.records.json_ref_loader import replace_refs
#from inspirehep.modules.authors.utils import scan_author_string_for_phrases
from nameparser import HumanName
import sys


def tei_response(record):
    
    data = record
    env = Environment(loader=PackageLoader('inspirehep.modules.converttohal',
                                           'templates'), trim_blocks=True, lstrip_blocks=True)
    template = env.get_template(TEMPLATE)
    #import ipdb; ipdb.set_trace()

    authors = data.get('authors', [])
    for author in authors:
        if 'full_name' in author and author['full_name']:
            parsed = HumanName(author['full_name'])
            author['parsed_name'] = parsed

    titles = data.get('titles', [])

    doi = data['dois'][0]['value'] if 'dois' in data else ""

    if 'publication_info' in data:
        pub_info = data['publication_info'][0]
        if 'journal_title' in pub_info:
            publication = _journal_data(pub_info)
        elif 'conference_record' in pub_info:
            publication = _conference_data(pub_info['conference_record'])
        else:
            publication = None
    else:
        publication = None

    my_affiliations = []
    seen = []
    structures = []
    for author in data.get('authors', []):
        for affiliation in author.get('affiliations', []):
            if 'recid' in affiliation and affiliation['recid'] not in seen:
                my_affiliations.append(affiliation)
                seen.append(affiliation['recid'])
    for affiliation in my_affiliations:
        ref = replace_refs(affiliation, 'db')

        if 'record' in ref and 'collections' in ref['record']:
            structures.append(
                _structure_data(ref['record'], affiliation['recid'])
            )

    print template.render(titles=titles, doi=doi, authors=authors,
                          publication=publication, structures=structures)

def _conference_data(conf):
    ref = replace_refs(conf, 'db')

    # FIXME: Add conference city, country, and country code fields

    return {'type': "conference",
            'name': ref['titles'][0]['title']
                if 'titles' in ref and 'title' in ref['titles'][0]
                else "",
            'acronym': ref['acronym'][0]
                if 'acronym' in ref
                else "",
            'opening_date': ref.get('opening_date', ""),
            'closing_date': ref.get('closing_date', "")}

def _journal_data(jour):
    if 'page_artid' in jour:
        pp = jour['page_artid']
    elif 'page_start' and 'page_end' in pub_info:
        pp = pub_info['page_start'] + "-" + pub_info['page_end']
    elif 'page_start' in pub_info or 'page_end' in pub_info:
        pp = pub_info['page_start'] or pub_info['page_end']
    else:
        pp = ""

    return {'type': "journal",
            'name': pub_info.get('journal_title', ""),
            'year': pub_info.get('year', ""),
            'volume': pub_info.get('journal_volume', ""),
            'issue': pub_info.get('journal_issue', ""),
            'pp': pp}   

'''
    Must pass recid separately because it cannot be found in the structure
    returned by replace_refs.
'''
def _structure_data(struct, recid):
    return {'type': struct['collections'][1]['primary'].lower()
                if len(struct['collections']) > 1
                    and 'primary' in struct['collections'][1]
                else "",
            'name': struct['institution'][0]
                if 'institution' in struct
                else "",
            'address': struct['address'][0]['original_address']
                if 'address' in struct
                    and 'original_address' in struct['address'][0]
                else [],
            'country': struct['address'][0]['country_code']
                if 'address' in struct
                    and 'country_code' in struct['address'][0]
                else "",
            'recid': recid}
    
