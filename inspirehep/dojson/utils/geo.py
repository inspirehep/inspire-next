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

from __future__ import absolute_import, division, print_function

import six

from inspirehep.utils.helpers import force_list


country_to_iso_code = {
    'AFGHANISTAN': 'AF',
    'ÅLAND ISLANDS': 'AX',
    'ALBANIA': 'AL',
    'ALGERIA': 'DZ',
    'AMERICAN SAMOA': 'AS',
    'ANDORRA': 'AD',
    'ANGOLA': 'AO',
    'ANGUILLA': 'AI',
    'ANTARCTICA': 'AQ',
    'ANTIGUA AND BARBUDA': 'AG',
    'ARGENTINA': 'AR',
    'ARMENIA': 'AM',
    'ARUBA': 'AW',
    'AUSTRALIA': 'AU',
    'AUSTRIA': 'AT',
    'AZERBAIJAN': 'AZ',
    'BAHAMAS': 'BS',
    'BAHRAIN': 'BH',
    'BANGLADESH': 'BD',
    'BARBADOS': 'BB',
    'BELARUS': 'BY',
    'BELGIUM': 'BE',
    'BELIZE': 'BZ',
    'BENIN': 'BJ',
    'BERMUDA': 'BM',
    'BHUTAN': 'BT',
    'BOLIVIA, PLURINATIONAL STATE OF': 'BO',
    'BONAIRE, SINT EUSTATIUS AND SABA': 'BQ',
    'BOSNIA AND HERZEGOVINA': 'BA',
    'BOTSWANA': 'BW',
    'BOUVET ISLAND': 'BV',
    'BRAZIL': 'BR',
    'BRITISH INDIAN OCEAN TERRITORY': 'IO',
    'BRUNEI DARUSSALAM': 'BN',
    'BULGARIA': 'BG',
    'BURKINA FASO': 'BF',
    'BURUNDI': 'BI',
    'CAMBODIA': 'KH',
    'CAMEROON': 'CM',
    'CANADA': 'CA',
    'CAPE VERDE': 'CV',
    'CAYMAN ISLANDS': 'KY',
    'CENTRAL AFRICAN REPUBLIC': 'CF',
    'CHAD': 'TD',
    'CHILE': 'CL',
    'CHINA': 'CN',
    'CHRISTMAS ISLAND': 'CX',
    'COCOS (KEELING) ISLANDS': 'CC',
    'COLOMBIA': 'CO',
    'COMOROS': 'KM',
    'CONGO': 'CG',
    'CONGO, THE DEMOCRATIC REPUBLIC OF THE': 'CD',
    'COOK ISLANDS': 'CK',
    'COSTA RICA': 'CR',
    'CÔTE D\'IVOIRE': 'CI',
    'CROATIA': 'HR',
    'CZECHOSLOVAKIA': 'CS',
    'CUBA': 'CU',
    'CURAÇAO': 'CW',
    'CYPRUS': 'CY',
    'CZECH REPUBLIC': 'CZ',
    'DENMARK': 'DK',
    'DJIBOUTI': 'DJ',
    'DOMINICA': 'DM',
    'DOMINICAN REPUBLIC': 'DO',
    'ECUADOR': 'EC',
    'EGYPT': 'EG',
    'EL SALVADOR': 'SV',
    'EQUATORIAL GUINEA': 'GQ',
    'ERITREA': 'ER',
    'ESTONIA': 'EE',
    'ETHIOPIA': 'ET',
    'FALKLAND ISLANDS (MALVINAS)': 'FK',
    'FAROE ISLANDS': 'FO',
    'FIJI': 'FJ',
    'FINLAND': 'FI',
    'FRANCE': 'FR',
    'FRENCH GUIANA': 'GF',
    'FRENCH POLYNESIA': 'PF',
    'FRENCH SOUTHERN TERRITORIES': 'TF',
    'GABON': 'GA',
    'GAMBIA': 'GM',
    'GEORGIA': 'GE',
    'GERMANY': 'DE',
    'GHANA': 'GH',
    'GIBRALTAR': 'GI',
    'GREECE': 'GR',
    'GREENLAND': 'GL',
    'GRENADA': 'GD',
    'GUADELOUPE': 'GP',
    'GUAM': 'GU',
    'GUATEMALA': 'GT',
    'GUERNSEY': 'GG',
    'GUINEA': 'GN',
    'GUINEA-BISSAU': 'GW',
    'GUYANA': 'GY',
    'HAITI': 'HT',
    'HEARD ISLAND AND MCDONALD ISLANDS': 'HM',
    'HOLY SEE (VATICAN CITY STATE)': 'VA',
    'HONDURAS': 'HN',
    'HONG KONG': 'HK',
    'HUNGARY': 'HU',
    'ICELAND': 'IS',
    'INDIA': 'IN',
    'INDONESIA': 'ID',
    'IRAN, ISLAMIC REPUBLIC OF': 'IR',
    'IRAQ': 'IQ',
    'IRELAND': 'IE',
    'ISLE OF MAN': 'IM',
    'ISRAEL': 'IL',
    'ITALY': 'IT',
    'JAMAICA': 'JM',
    'JAPAN': 'JP',
    'JERSEY': 'JE',
    'JORDAN': 'JO',
    'KAZAKHSTAN': 'KZ',
    'KENYA': 'KE',
    'KIRIBATI': 'KI',
    'KOREA, DEMOCRATIC PEOPLE\'S REPUBLIC OF': 'KP',
    'KOREA, REPUBLIC OF': 'KR',
    'KUWAIT': 'KW',
    'KYRGYZSTAN': 'KG',
    'LAO PEOPLE\'S DEMOCRATIC REPUBLIC': 'LA',
    'LATVIA': 'LV',
    'LEBANON': 'LB',
    'LESOTHO': 'LS',
    'LIBERIA': 'LR',
    'LIBYA': 'LY',
    'LIECHTENSTEIN': 'LI',
    'LITHUANIA': 'LT',
    'LUXEMBOURG': 'LU',
    'MACAO': 'MO',
    'MACEDONIA, THE FORMER YUGOSLAV REPUBLIC OF': 'MK',
    'MADAGASCAR': 'MG',
    'MALAWI': 'MW',
    'MALAYSIA': 'MY',
    'MALDIVES': 'MV',
    'MALI': 'ML',
    'MALTA': 'MT',
    'MARSHALL ISLANDS': 'MH',
    'MARTINIQUE': 'MQ',
    'MAURITANIA': 'MR',
    'MAURITIUS': 'MU',
    'MAYOTTE': 'YT',
    'MEXICO': 'MX',
    'MICRONESIA, FEDERATED STATES OF': 'FM',
    'MOLDOVA, REPUBLIC OF': 'MD',
    'MONACO': 'MC',
    'MONGOLIA': 'MN',
    'MONTENEGRO': 'ME',
    'MONTSERRAT': 'MS',
    'MOROCCO': 'MA',
    'MOZAMBIQUE': 'MZ',
    'MYANMAR': 'MM',
    'NAMIBIA': 'NA',
    'NAURU': 'NR',
    'NEPAL': 'NP',
    'NEUTRAL ZONE': 'NT',
    'NETHERLANDS': 'NL',
    'NETHERLADS ANTILLES': 'AN',
    'NEW CALEDONIA': 'NC',
    'NEW ZEALAND': 'NZ',
    'NICARAGUA': 'NI',
    'NIGER': 'NE',
    'NIGERIA': 'NG',
    'NIUE': 'NU',
    'NORFOLK ISLAND': 'NF',
    'NORTHERN MARIANA ISLANDS': 'MP',
    'NORWAY': 'NO',
    'OMAN': 'OM',
    'PAKISTAN': 'PK',
    'PALAU': 'PW',
    'PALESTINE, STATE OF': 'PS',
    'PANAMA': 'PA',
    'PAPUA NEW GUINEA': 'PG',
    'PARAGUAY': 'PY',
    'PERU': 'PE',
    'PHILIPPINES': 'PH',
    'PITCAIRN': 'PN',
    'POLAND': 'PL',
    'PORTUGAL': 'PT',
    'PUERTO RICO': 'PR',
    'QATAR': 'QA',
    'RÉUNION': 'RE',
    'ROMANIA': 'RO',
    'RUSSIAN FEDERATION': 'RU',
    'RWANDA': 'RW',
    'SAINT BARTHÉLEMY': 'BL',
    'SAINT HELENA, ASCENSION AND TRISTAN DA CUNHA': 'SH',
    'SAINT KITTS AND NEVIS': 'KN',
    'SAINT LUCIA': 'LC',
    'SAINT MARTIN (FRENCH PART)': 'MF',
    'SAINT PIERRE AND MIQUELON': 'PM',
    'SAINT VINCENT AND THE GRENADINES': 'VC',
    'SAMOA': 'WS',
    'SAN MARINO': 'SM',
    'SAO TOME AND PRINCIPE': 'ST',
    'SAUDI ARABIA': 'SA',
    'SENEGAL': 'SN',
    'SERBIA': 'RS',
    'SERBIA AND MONTENEGRO': 'AB',
    'SEYCHELLES': 'SC',
    'SIERRA LEONE': 'SL',
    'SINGAPORE': 'SG',
    'SINT MAARTEN (DUTCH PART)': 'SX',
    'SLOVAKIA': 'SK',
    'SLOVENIA': 'SI',
    'SOLOMON ISLANDS': 'SB',
    'SOMALIA': 'SO',
    'SOUTH AFRICA': 'ZA',
    'SOUTH GEORGIA AND THE SOUTH SANDWICH ISLANDS': 'GS',
    'SOUTH SUDAN': 'SS',
    'SPAIN': 'ES',
    'SRI LANKA': 'LK',
    'SUDAN': 'SD',
    'SURINAME': 'SR',
    'SVALBARD AND JAN MAYEN': 'SJ',
    'SWAZILAND': 'SZ',
    'SWEDEN': 'SE',
    'SWITZERLAND': 'CH',
    'SYRIAN ARAB REPUBLIC': 'SY',
    'TAIWAN, PROVINCE OF CHINA': 'TW',
    'TAJIKISTAN': 'TJ',
    'TANZANIA, UNITED REPUBLIC OF': 'TZ',
    'THAILAND': 'TH',
    'TIMOR-LESTE': 'TL',
    'TOGO': 'TG',
    'TOKELAU': 'TK',
    'TONGA': 'TO',
    'TRINIDAD AND TOBAGO': 'TT',
    'TUNISIA': 'TN',
    'TURKEY': 'TR',
    'TURKMENISTAN': 'TM',
    'TURKS AND CAICOS ISLANDS': 'TC',
    'TUVALU': 'TV',
    'UGANDA': 'UG',
    'UKRAINE': 'UA',
    'UNITED ARAB EMIRATES': 'AE',
    'UNITED KINGDOM': 'GB',
    'UNITED STATES': 'US',
    'UNITED STATES MINOR OUTLYING ISLANDS': 'UM',
    'URUGUAY': 'UY',
    'USSR': 'SU',
    'UZBEKISTAN': 'UZ',
    'VANUATU': 'VU',
    'VENEZUELA, BOLIVARIAN REPUBLIC OF': 'VE',
    'VIET NAM': 'VN',
    'VIRGIN ISLANDS, BRITISH': 'VG',
    'VIRGIN ISLANDS, U.S.': 'VI',
    'WALLIS AND FUTUNA': 'WF',
    'WESTERN SAHARA': 'EH',
    'YEMEN': 'YE',
    'YUGOSLAVIA': 'YU',
    'ZAMBIA': 'ZM',
    'ZIMBABWE': 'ZW',
}

iso_code_to_country_name = {v: k for k, v in country_to_iso_code.items()}

countries_alternative_codes = {
    'CN': ['CHINA'],
    'FI': ['FN'],
    'FR': ['FX'],
    'GB': ['UK'],
    'TL': ['TP'],
    'CD': ['ZR']
}

countries_alternative_spellings = {
    'AU': ['SAUSTRALIA'],
    'AM': ['REPUBLIC OF ARMENIA'],
    'BA': ['BOSNIA-HERZEGOVINA', 'BOSNIA'],
    'BH': ['KINGDOM OF BAHRAIN'],
    'BJ': ['REPUBLIC OF BENIN'],
    'BO': ['BOLIVIA'],
    'BR': ['BRASIL', 'SC BRAZIL'],
    'CA': ['BC CANADA', 'BRITISH COLUMBIA'],
    'CH': ['SWITZ', 'SWITZLERAND', 'SWITZERLAND (CERN)', 'SWITERLAND'],
    'CN': ['PR CHINA'],
    'CS': ['CZECHSOLVAKIA'],
    'CZ': ['PRAGUE'],
    'DE': ['DEUTSCHLAND', 'WEST GERMANY', 'EAST GERMANY', 'BAVARIA',
           'GERMANY (DESY)'],
    'ES': ['CANARY ISLANDS', 'MADRID'],
    'FR': ['CORSICA'],
    'GR': ['CRETE'],
    'GB': ['UK', 'ENGLAND', 'ENG', 'SCOTLAND', 'WALES', 'SCOTLAND/UK',
           'NORTHERN IRELAND', 'LONDON'],
    'ID': ['BALI'],
    'IL': ['JERUSALEM'],
    'IR': ['IRAN'],
    'IT': ['ITALIE', 'ITALIA', 'NAPOLI', 'MESSINA', 'SARDINIA', 'SICILY'],
    'KR': ['SOUTH KOREA', 'SOUTH-KOREA', 'REPUBLIC OF KOREA'],
    'NL': ['THE NETHERLANDS', 'NEDERLANDS', 'NETHERLANDS'],
    'SU': ['SOVIET UNION'],
    'RS': ['REPUBLIC OF SERBIA'],
    'RU': ['RUSSIA', 'RUSSI', 'RUSSIA FEDERATION'],
    'SK': ['SLOVAK REPUBLIC'],
    'TW': ['TAIWAN'],
    'YU': ['YUGOSL', 'YU'],
    'VE': ['VENEZUELA'],
    'VN': ['VIETNAM'],
    'US': ['UNITED STATES OF AMERICA', 'UNITED STATES', 'US', 'USA'],
    'ZA': ['SAFRICA']
}


us_state_to_iso_code = {
    'ALABAMA': 'AL',
    'ALASKA': 'AK',
    'ARIZONA': 'AZ',
    'ARKANSAS': 'AR',
    'CALIFORNIA': 'CA',
    'COLORADO': 'CO',
    'CONNECTICUT': 'CT',
    'DELAWARE': 'DE',
    'DISTRICT OF COLUMBIA': 'DC',
    'FLORIDA': 'FL',
    'GEORGIA': 'GA',
    'HAWAII': 'HI',
    'IDAHO': 'ID',
    'ILLINOIS': 'IL',
    'INDIANA': 'IN',
    'IOWA': 'IA',
    'KANSAS': 'KS',
    'KENTUCKY': 'KY',
    'LOUISIANA': 'LA',
    'MAINE': 'ME',
    'MARYLAND': 'MD',
    'MASSACHUSETTS': 'MA',
    'MICHIGAN': 'MI',
    'MINNESOTA': 'MN',
    'MISSISSIPPI': 'MS',
    'MISSOURI': 'MO',
    'MONTANA': 'MT',
    'NEBRASKA': 'NE',
    'NEVADA': 'NV',
    'NEW HAMPSHIRE': 'NH',
    'NEW JERSEY': 'NJ',
    'NEW MEXICO': 'NM',
    'NEW YORK': 'NY',
    'NORTH CAROLINA': 'NC',
    'NORTH DAKOTA': 'ND',
    'OHIO': 'OH',
    'OKLAHOMA': 'OK',
    'OREGON': 'OR',
    'PENNSYLVANIA': 'PA',
    'RHODE ISLAND': 'RI',
    'SOUTH CAROLINA': 'SC',
    'SOUTH DAKOTA': 'SD',
    'TENNESSEE': 'TN',
    'TEXAS': 'TX',
    'UTAH': 'UT',
    'VERMONT': 'VT',
    'VIRGINIA': 'VA',
    'WASHINGTON': 'WA',
    'WEST VIRGINIA': 'WV',
    'WISCONSIN': 'WI',
    'WYOMING': 'WY'
}

us_states_alternative_spellings = {
    'AL': ['AL', 'ALA'],
    'AK': ['AK'],
    'AZ': ['AZ', 'ARIZ'],
    'AR': ['AR'],
    'CA': ['CA', 'CALIFORNIA', 'CALIF', 'CALF'],
    'CO': ['CO', 'COLO'],
    'CT': ['CT', 'CONNETICUT'],
    'DC': ['DC'],
    'DE': ['DE', 'DEL'],
    'FL': ['FL'],
    'GA': ['GA'],
    'HI': ['HI'],
    'ID': ['ID'],
    'IL': ['IL', 'ILL', 'ILLINOIS'],
    'IN': ['IN'],
    'IA': ['IA'],
    'KS': ['KS'],
    'KY': ['KY'],
    'LA': ['LA'],
    'ME': ['ME'],
    'MD': ['MD'],
    'MA': ['MA', 'MASS'],
    'MI': ['MI', 'MICH'],
    'MN': ['MN'],
    'MS': ['MS'],
    'MO': ['MO'],
    'MT': ['MT'],
    'NE': ['NE', 'NEV'],
    'NV': ['NV'],
    'NH': ['NH'],
    'NJ': ['NJ'],
    'NM': ['NM', 'NMEX', 'NEW MEXIKO', 'NEW MEX', 'N MEX', 'NEW MEXICO'],
    'NY': ['NY'],
    'NC': ['NC'],
    'ND': ['ND'],
    'OH': ['OH'],
    'OK': ['OK'],
    'OR': ['OR'],
    'PA': ['PA'],
    'RI': ['RI'],
    'SC': ['SC'],
    'SD': ['SD'],
    'TN': ['TN', 'TENN'],
    'TX': ['TX', 'TEX'],
    'UT': ['UT'],
    'VT': ['VT'],
    'VA': ['VA'],
    'WA': ['WA'],
    'WV': ['WV'],
    'WI': ['WI', 'WIS', 'WISC'],
    'WY': ['WY'],
}

south_korean_cities = ['SEOUL', 'DAEJON', 'DAEJEON', 'MT SORAK', 'POHANG',
                       'JEJU ISLAND', 'CHEJU ISLAND', 'GYEONGJU', 'BUSAN',
                       'DAEGU', 'GYEONGIU', 'PUSAN', 'YONGPYONG',
                       'PHOENIX PARK', 'CHEJU ISLAND']


def match_country_code(original_code):
    if isinstance(original_code, six.string_types):
        original_code = original_code.upper()
        if iso_code_to_country_name.get(original_code):
            return original_code
        else:
            for country_code, alternatives in countries_alternative_codes.items():
                for alternative in alternatives:
                    if original_code == alternative:
                        return country_code
            return None
    else:
        return None


def match_country_name_to_its_code(country_name, city=''):
    """Try to match country name with its code.

    Name of the city helps when country_name is "Korea".
    """
    if country_name:
        country_name = country_name.upper().replace('.', '').strip()

        if country_to_iso_code.get(country_name):
            return country_to_iso_code.get(country_name)
        elif country_name == 'KOREA':
            if city.upper() in south_korean_cities:
                return 'KR'
        else:
            for c_code, spellings in countries_alternative_spellings.items():
                for spelling in spellings:
                    if country_name == spelling:
                        return c_code

    return None


def match_us_state(state_string):
    """Try to match a string with one of the states in the US."""
    if state_string:
        state_string = state_string.upper().replace('.', '').strip()
        if us_state_to_iso_code.get(state_string):
            return us_state_to_iso_code.get(state_string)
        else:
            for code, state_spellings in us_states_alternative_spellings.items():
                for spelling in state_spellings:
                    if state_string == spelling:
                        return code
    return None


def parse_conference_address(address_string):
    """Parse a conference address.

    This is a pretty dummy address parser. It only extracts country
    and state (for US) and should be replaced with something better,
    like Google Geocoding.
    """

    geo_elements = address_string.split(',')
    city = geo_elements[0]
    country_name = geo_elements[-1].upper().replace('.', '').strip()
    us_state = None
    state = None
    country_code = None

    # Try to match the country
    country_code = match_country_name_to_its_code(country_name, city)

    if country_code == 'US' and len(geo_elements) > 1:
        us_state = match_us_state(geo_elements[-2].upper().strip()
                                  .replace('.', ''))

    if not country_code:
        # Sometimes the country name stores info about U.S. state
        us_state = match_us_state(country_name)

    if us_state:
        state = us_state
        country_code = 'US'

    return {
        'cities': [
            city,
        ],
        'country_code': country_code,
        'postal_address': force_list(address_string),
        'postal_code': None,
        'state': state,
    }


def parse_institution_address(address, city, state_province,
                              country, postal_code, country_code):
    """Parse an institution address."""
    address_list = force_list(address)
    state_province = match_us_state(state_province) or state_province

    postal_code = force_list(postal_code)
    country = force_list(country)
    country_code = match_country_code(country_code)

    if isinstance(postal_code, (tuple, list)):
        postal_code = ', '.join(postal_code)

    if isinstance(country, (tuple, list)):
        country = ', '.join(set(country))

    if not country_code and country:
        country_code = match_country_name_to_its_code(country)

    if not country_code and state_province and state_province in us_state_to_iso_code.values():
        country_code = 'US'

    return {
        'cities': force_list(city),
        'country_code': country_code,
        'postal_address': address_list,
        'postal_code': postal_code,
        'state': state_province,
    }
