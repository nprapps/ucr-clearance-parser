#!/usr/bin/env python

import csv
import locale
import logging
import re
import sys

SECTION_BREAK = 'CLEARANCE RATE DATA FOR INDEX OFFENSES'
END_BREAK = '  READ'
FIELDNAMES = ['state', 'lea_code', 'lea_name', 'population', 'mos', 'agg_assault_cleared', 'agg_assault_cleared_pct', 'agg_assault_count', 'arson_cleared', 'arson_cleared_pct', 'arson_count', 'burglary_cleared', 'burglary_cleared_pct', 'burglary_count', 'forcible_rape_cleared', 'forcible_rape_cleared_pct', 'forcible_rape_count', 'larceny_theft_cleared', 'larceny_theft_cleared_pct', 'larceny_theft_count', 'murder_cleared', 'murder_cleared_pct', 'murder_count', 'mvt_cleared', 'mvt_cleared_pct', 'mvt_count', 'property_cleared', 'property_cleared_pct', 'property_count', 'robbery_cleared', 'robbery_cleared_pct', 'robbery_count', 'violent_cleared', 'violent_cleared_pct', 'violent_count']

locale.setlocale(locale.LC_ALL, 'en_US')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ucr-parser')

def parse(file_path):
    output = {}
    f = open(file_path)

    line = _skip_to_start(f)

    while True:
        row = {}
        for i in range(0, 4):

            if SECTION_BREAK in line:
                line = _skip_section_break(f)

            # We're done!
            if END_BREAK in line:
                return output

            line_parts = _split_line(line)

            if i == 0:
                row['lea_code'] = line_parts[0]
                row['lea_name'] = line_parts[1]

                if row['lea_code'][0].isdigit():
                    row['state'] = row['lea_code'][1:3]
                else:
                    row['state'] = row['lea_code'][0:2]

            if i == 1:
                row['mos'] = locale.atoi(line_parts[0])
                row['violent_count'] = locale.atoi(line_parts[3])
                row['property_count'] = locale.atoi(line_parts[4])
                row['murder_count'] = locale.atoi(line_parts[5])
                row['forcible_rape_count'] = locale.atoi(line_parts[6])
                row['robbery_count'] = locale.atoi(line_parts[7])
                row['agg_assault_count'] = locale.atoi(line_parts[8])
                row['burglary_count'] = locale.atoi(line_parts[9])
                row['larceny_theft_count'] = locale.atoi(line_parts[10])
                row['mvt_count'] = locale.atoi(line_parts[11])
                row['arson_count'] = locale.atoi(line_parts[12])

            if i == 2:
                row['population'] = locale.atoi(line_parts[0])
                row['violent_cleared'] = locale.atoi(line_parts[3])
                row['property_cleared'] = locale.atoi(line_parts[4])
                row['murder_cleared'] = locale.atoi(line_parts[5])
                row['forcible_rape_cleared'] = locale.atoi(line_parts[6])
                row['robbery_cleared'] = locale.atoi(line_parts[7])
                row['agg_assault_cleared'] = locale.atoi(line_parts[8])
                row['burglary_cleared'] = locale.atoi(line_parts[9])
                row['larceny_theft_cleared'] = locale.atoi(line_parts[10])
                row['mvt_cleared'] = locale.atoi(line_parts[11])
                row['arson_cleared'] = locale.atoi(line_parts[12])

            if i == 3:
                row['violent_cleared_pct'] = float(line_parts[1])
                row['property_cleared_pct'] = float(line_parts[2])
                row['murder_cleared_pct'] = float(line_parts[3])
                row['forcible_rape_cleared_pct'] = float(line_parts[4])
                row['robbery_cleared_pct'] = float(line_parts[5])
                row['agg_assault_cleared_pct'] = float(line_parts[6])
                row['burglary_cleared_pct'] = float(line_parts[7])
                row['larceny_theft_cleared_pct'] = float(line_parts[8])
                row['mvt_cleared_pct'] = float(line_parts[9])
                row['arson_cleared_pct'] = float(line_parts[10])

            line = f.readline()

        if row['state'] not in output.keys():
            output[row['state']] = []

        output[row['state']].append(row)


def _skip_to_start(f):
    """
    Skip to start of data
    """
    while True:
        line = f.readline()
        if SECTION_BREAK in line:
            break
    return line


def _skip_section_break(f):
    """
    Read three lines
    """
    f.readline()
    f.readline()
    f.readline()
    return f.readline()


def _split_line(line):
    return re.sub(' +', ' ', line).strip().split(' ')


if __name__ == '__main__':
    output = parse(sys.argv[1])
    for state, rows in output.items():
        filename = 'data/%s-%s-clearance.csv' % (state, sys.argv[2])
        with open(filename, 'w') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=FIELDNAMES)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
