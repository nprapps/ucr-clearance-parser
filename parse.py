#!/usr/bin/env python

import csv
import locale
import logging
import re
import sys

from itertools import groupby

SECTION_BREAK = 'CLEARANCE RATE DATA FOR INDEX OFFENSES'
END_BREAK = '  READ'
FIELDNAMES = ['state', 'lea_code', 'lea_name', 'population', 'mos', 'agg_assault_cleared', 'agg_assault_cleared_pct', 'agg_assault_count', 'arson_cleared', 'arson_cleared_pct', 'arson_count', 'burglary_cleared', 'burglary_cleared_pct', 'burglary_count', 'forcible_rape_cleared', 'forcible_rape_cleared_pct', 'forcible_rape_count', 'larceny_theft_cleared', 'larceny_theft_cleared_pct', 'larceny_theft_count', 'murder_cleared', 'murder_cleared_pct', 'murder_count', 'mvt_cleared', 'mvt_cleared_pct', 'mvt_count', 'property_cleared', 'property_cleared_pct', 'property_count', 'robbery_cleared', 'robbery_cleared_pct', 'robbery_count', 'violent_cleared', 'violent_cleared_pct', 'violent_count']

locale.setlocale(locale.LC_ALL, 'en_US')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ucr-parser')

def parse(file_path):
    output = []
    f = open(file_path)

    line = skip_to_start(f)

    while True:
        row = {}
        for i in range(0, 4):

            if SECTION_BREAK in line:
                line = skip_section_break(f)

            # We're done!
            if END_BREAK in line:
                return output

            line_parts = split_line(line)

            if i == 0:
                row['lea_code'] = line_parts[0]
                row['lea_name'] = line_parts[1]

                row['state'] = parse_state(row['lea_code'])

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
    if value[0].isdigit():
        return value[1:3]
    else:
        return value[0:2]


def write_csv(data, filename):
    """
    Write a CSV from a list of dicts
    """
    with open(filename, 'w') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


if __name__ == '__main__':
    data = parse(sys.argv[1])
    write_csv(data, 'data/%s-all_states-clearance.csv' % sys.argv[2])
    for state, state_data in groupby(data, lambda x: x['state']):
        filename = 'data/%s-%s-clearance.csv' % (state, sys.argv[2])
        write_csv(state_data, filename)
