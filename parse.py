#!/usr/bin/env python

import logging
import re
import sys

SECTION_BREAK = 'CLEARANCE RATE DATA FOR INDEX OFFENSES'
END_BREAK = '  READ'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ucr-parser')

def parse(file_path):
    with open(file_path) as f:
        # Skip to first section
        for line in f:
            if SECTION_BREAK in line:
                logger.info('Found first data line, processing')
                break

        for line in f:
            if line.startswith(END_BREAK):
                logger.info('Found last data line, done')
                break
            if SECTION_BREAK not in line:
                process_line(line)


def process_line(line):
    logger.info(line)
    return line


if __name__ == '__main__':
    parse(sys.argv[1])
