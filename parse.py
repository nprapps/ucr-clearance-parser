#!/usr/bin/env python

import csv
import dataset
import json
import locale
import logging
import re
import sys

from collections import OrderedDict
from itertools import groupby

SECTION_BREAK = 'CLEARANCE RATE DATA FOR INDEX OFFENSES'
END_BREAK = '  READ'
FIELDNAMES = ['year', 'state', 'ori7', 'lea_name', 'population', 'mos', 'agg_assault_cleared', 'agg_assault_cleared_pct', 'agg_assault_count', 'arson_cleared', 'arson_cleared_pct', 'arson_count', 'burglary_cleared', 'burglary_cleared_pct', 'burglary_count', 'forcible_rape_cleared', 'forcible_rape_cleared_pct', 'forcible_rape_count', 'larceny_theft_cleared', 'larceny_theft_cleared_pct', 'larceny_theft_count', 'murder_cleared', 'murder_cleared_pct', 'murder_count', 'mvt_cleared', 'mvt_cleared_pct', 'mvt_count', 'property_cleared', 'property_cleared_pct', 'property_count', 'robbery_cleared', 'robbery_cleared_pct', 'robbery_count', 'violent_cleared', 'violent_cleared_pct', 'violent_count']

CRIME_TYPES = [
    'violent',
    'property',
    'murder',
    #'forcible_rape',
    'robbery',
    'agg_assault',
    'burglary',
    'larceny_theft',
    'mvt',
    'arson',
]

IMPORT_FILES = [
    ('2011', '2011-clearance-rates.txt'),
    ('2012', '2012-clearance-rates.txt'),
    ('2013', '2013-clearance-rates.txt'),
]

POPULATION_BUCKETS = [
    {
        'name': '1,000,000 and above',
        'low': 1000000,
        'high': None,
    },
    {
        'name': '500,000 to 999,999',
        'low': 500000,
        'high': 999999,
    },
    {
        'name': '250,000 to 499,999',
        'low': 250000,
        'high': 499999,
    },
    {
        'name': '100,000 to 249,999',
        'low': 100000,
        'high': 249999,
    },
    {
        'name': '50,000 to 99,999',
        'low': 50000,
        'high': 99999,
    },
    {
        'name': '25,000 to 49,999',
        'low': 25000,
        'high': 49999,
    },

    {
        'name': '10,000 to 24,999',
        'low': 10000,
        'high': 24999,
    },
    {
        'name': 'Under 10,000',
        'low': 1,  # Population should never be 0
        'high': 9999,
    },
]

locale.setlocale(locale.LC_ALL, 'en_US')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ucr-parser')

db = dataset.connect('postgresql:///ucr_clearance')

def parse(file_path, year):
    output = []
    f = open(file_path)

    line = skip_to_start(f)

    while True:
        row = {
            'year': year
        }
        for i in range(0, 4):

            if SECTION_BREAK in line:
                line = skip_section_break(f)

            # We're done!
            if END_BREAK in line:
                return output

            line_parts = split_line(line)

            if i == 0:
                row['ori7'] = line_parts[0]
                if row['ori7'].startswith('0'):
                    row['ori7'] = row['ori7'][1:]
                row['lea_name'] = ' '.join(line_parts[1:])

                row['state'] = parse_state(row['ori7'])

            if i == 1:
                row['mos'] = parse_int(line_parts[0])
                row['violent_count'] = parse_int(line_parts[3])
                row['property_count'] = parse_int(line_parts[4])
                row['murder_count'] = parse_int(line_parts[5])
                row['forcible_rape_count'] = parse_int(line_parts[6])
                row['robbery_count'] = parse_int(line_parts[7])
                row['agg_assault_count'] = parse_int(line_parts[8])
                row['burglary_count'] = parse_int(line_parts[9])
                row['larceny_theft_count'] = parse_int(line_parts[10])
                row['mvt_count'] = parse_int(line_parts[11])
                row['arson_count'] = parse_int(line_parts[12])

            if i == 2:
                row['population'] = parse_int(line_parts[0])
                row['violent_cleared'] = parse_int(line_parts[3])
                row['property_cleared'] = parse_int(line_parts[4])
                row['murder_cleared'] = parse_int(line_parts[5])
                row['forcible_rape_cleared'] = parse_int(line_parts[6])
                row['robbery_cleared'] = parse_int(line_parts[7])
                row['agg_assault_cleared'] = parse_int(line_parts[8])
                row['burglary_cleared'] = parse_int(line_parts[9])
                row['larceny_theft_cleared'] = parse_int(line_parts[10])
                row['mvt_cleared'] = parse_int(line_parts[11])
                row['arson_cleared'] = parse_int(line_parts[12])

            if i == 3:
                row['violent_cleared_pct'] = parse_pct(line_parts[1])
                row['property_cleared_pct'] = parse_pct(line_parts[2])
                row['murder_cleared_pct'] = parse_pct(line_parts[3])
                row['forcible_rape_cleared_pct'] = parse_pct(line_parts[4])
                row['robbery_cleared_pct'] = parse_pct(line_parts[5])
                row['agg_assault_cleared_pct'] = parse_pct(line_parts[6])
                row['burglary_cleared_pct'] = parse_pct(line_parts[7])
                row['larceny_theft_cleared_pct'] = parse_pct(line_parts[8])
                row['mvt_cleared_pct'] = parse_pct(line_parts[9])
                row['arson_cleared_pct'] = parse_pct(line_parts[10])

            line = f.readline()

        logger.debug('Writing row for %s (%s), %s' % (row['ori7'], row['lea_name'], year))
        output.append(row)


def skip_to_start(f):
    """
    Skip to start of data
    """
    while True:
        line = f.readline()
        if SECTION_BREAK in line:
            break
    return line


def skip_section_break(f):
    """
    Read four lines after section break
    """
    f.readline()
    f.readline()
    f.readline()
    return f.readline()


def split_line(line):
    return re.sub(' +', ' ', line).strip().split(' ')


def parse_pct(value):
    """
    Parse percentage
    """
    return float(value)/100


def parse_int(value):
    """
    Parse integer
    """
    return locale.atoi(value)


def parse_state(value):
    """
    Parse state from LEA code.
    """
    return value[0:2]


def get_data():
    """
    Get and parse raw data
    """
    all_data = []

    for year, file in IMPORT_FILES:
        data_file = 'data/%s' % file
        data = parse(data_file, year)
        all_data = all_data + data

    return all_data

def get_agencies():
    """
    Get agency data
    """
    agencies = {}
    with open('data/agency-crosswalk.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            agencies[row['ORI7']] = row

    return agencies


def write_agency_lookup():
    """
    Write agency lookup
    """
    result = db.query("""
        select
        a.ori7, a.agency, a.agentype, a.state
        from agencies as a join clearance_rates as c on a.ori7 = c.ori7
        group by a.ori7, a.agency, a.agentype, a.state
        order by a.ori7
    """)
    dataset.freeze(result, format='csv', filename='output/agency_names.csv')


def write_clearance_json():
    """
    Write json data
    """
    result = db.query("""
        select
        a.ori7, a.agency, a.state, a.agentype,
        c.year, c.population, c.mos,
        c.violent_count, c.violent_cleared, c.violent_cleared_pct,
        c.property_count, c.property_cleared, c.property_cleared_pct,
        c.murder_count, c.murder_cleared, c.murder_cleared_pct,
        c.forcible_rape_count, c.forcible_rape_cleared, c.forcible_rape_cleared_pct,
        c.robbery_count, c.robbery_cleared, c.robbery_cleared_pct,
        c.agg_assault_count, c.agg_assault_cleared, c.agg_assault_cleared_pct,
        c.burglary_count, c.burglary_cleared, c.burglary_cleared_pct,
        c.mvt_count, c.mvt_cleared, c.mvt_cleared_pct,
        c.larceny_theft_count, c.larceny_theft_cleared, c.larceny_theft_cleared_pct,
        c.arson_count, c.arson_cleared, c.arson_cleared_pct
        from clearance_rates as c join agencies as a on a.ori7 = c.ori7
        order by c.ori7, c.year
    """)

    medians = analyze_medians()

    data = []
    for row in result:
        data.append(row)

    for ori7, yearly_data in groupby(data, lambda x: x['ori7']):
        output = {
            'ori7': ori7,
            'crimes': OrderedDict(),
        }
        for row in yearly_data:
            year = row['year']

            has_median = False
            if row['agentype'] == 'Municipal police':
                has_median = True
                bucket = get_population_bucket(row['population'])
                if bucket and not output.get('medians'):
                    output['medians'] = OrderedDict()

            if not output.get('agency'):
                output['agency'] = row['agency']
                output['state'] = row['state']
                output['agency_type'] = row['agentype']


            if year == '2013' and has_median and bucket:
                output['population_bucket'] = bucket
                output['population'] = row['population']

            for field in CRIME_TYPES:
                if not output['crimes'].get(field):
                    output['crimes'][field] = {}

                if has_median and bucket:
                    if not output['medians'].get(field):
                        output['medians'][field] = {}
                    output['medians'][field][year] = {}

                output['crimes'][field][year] = {}
                output['crimes'][field][year]['mos'] = row['mos']

                for measure in ['count', 'cleared', 'cleared_pct']:
                    output['crimes'][field][year][measure] = row['%s_%s' % (field, measure)]
                    if output.get('medians') and bucket:
                        median_key = 'median_%s_%s' % (field, measure)
                        median_value = medians[year][bucket][median_key]
                        output['medians'][field][year][measure] = median_value

        with open('output/%s.json' % ori7, 'w') as outfile:
            logger.debug('Writing output/%s.json' % ori7)
            json.dump(output, outfile)


def get_population_bucket(population):
    """
    Get population bucket
    """
    for bucket in POPULATION_BUCKETS:
        if bucket['high']:
            if population >= bucket['low'] and population <= bucket['high']:
                return bucket['name']
        else:
            if population >= bucket['low']:
                return bucket['name']

    return None


def analyze_medians():
    """
    Analyze medians
    """
    # Output is per-year, per-bucket, per-crime-type
    output = {}

    # Loop over years
    for year, filename in IMPORT_FILES:
        output[year] = {}
        for bucket in POPULATION_BUCKETS:

            where = 'population >= %d' % bucket['low']
            if bucket['high']:
                where = '%s and population <= %d' % (where, bucket['high'])

            result = db.query("""
                select
                median(violent_count) as median_violent_count,
                median(violent_cleared) as median_violent_cleared,
                median(violent_cleared_pct) as median_violent_cleared_pct,
                median(property_count) as median_property_count,
                median(property_cleared) as median_property_cleared,
                median(property_cleared_pct) as median_property_cleared_pct,
                median(murder_count) as median_murder_count,
                median(murder_cleared) as median_murder_cleared,
                median(murder_cleared_pct) as median_murder_cleared_pct,
                median(robbery_count) as median_robbery_count,
                median(robbery_cleared) as median_robbery_cleared,
                median(robbery_cleared_pct) as median_robbery_cleared_pct,
                median(agg_assault_count) as median_agg_assault_count,
                median(agg_assault_cleared) as median_agg_assault_cleared,
                median(agg_assault_cleared_pct) as median_agg_assault_cleared_pct,
                median(burglary_count) as median_burglary_count,
                median(burglary_cleared) as median_burglary_cleared,
                median(burglary_cleared_pct) as median_burglary_cleared_pct,
                median(mvt_count) as median_mvt_count,
                median(mvt_cleared) as median_mvt_cleared,
                median(mvt_cleared_pct) as median_mvt_cleared_pct,
                median(larceny_theft_count) as median_larceny_theft_count,
                median(larceny_theft_cleared) as median_larceny_theft_cleared,
                median(larceny_theft_cleared_pct) as median_larceny_theft_cleared_pct,
                median(arson_count) as median_arson_count,
                median(arson_cleared) as median_arson_cleared,
                median(arson_cleared_pct) as median_arson_cleared_pct
                from clearance_rates as c join agencies as a on a.ori7 = c.ori7
                where mos=12 and year='%s'
                      and a.agentype='Municipal police'
                      and %s
            """ % (year, where))

            data = []
            for row in result:
                data.append(row)

            output[year][bucket['name']] = data[0]

    return output


def write_rates_to_db(data):
    """
    Write clearance rate data to db
    """
    logger.info('writing rates')
    table = db['clearance_rates']
    table.insert_many(data)


def write_agencies_to_db(agencies):
    """
    Write agency data to db
    """
    logger.info('writing agencies')
    table = db['agencies']

    process_agencies = []
    for agency in agencies.values():
        if not agency.get('ORI7'):
            continue

        processed_agency = {}
        for key, value in agency.items():
            # Skip the empty column whose meaning is not known
            if key != '':
                processed_agency[key.lower()] = value

        process_agencies.append(processed_agency)

    table.insert_many(process_agencies)


if __name__ == '__main__':
    logger.info('Parsing agency data')
    agencies = get_agencies()
    logger.info('Writing agency data to db')
    write_agencies_to_db(agencies)

    logger.info('Parsing clearance data')
    data = get_data()
    logger.info('Writing clearance data to db')
    write_rates_to_db(data)

    logger.info('Writing agency lookup')
    write_agency_lookup()

    logger.info('Writing individual JSON files')
    write_clearance_json()
