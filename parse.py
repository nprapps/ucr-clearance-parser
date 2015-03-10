#!/usr/bin/env python

import logging
import re
import sys

SECTION_BREAK = 'CLEARANCE RATE DATA FOR INDEX OFFENSES'
END_BREAK = '  READ'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ucr-parser')

def parse(file_path):
    output = []
    line = True
    with open(file_path) as f:
        while line:
            line = f.readline()
            logger.info(line)
        
        # Skip to first section
        #for line in f:
            #if SECTION_BREAK in line:
                #logger.info('Found first data line, processing')
                #break

        #for line in f:
            #if line.startswith(END_BREAK):
                #logger.info('Found last data line, done')
                #break

            
            #line = re.sub(' +', ' ', line).strip()
            #logger.info(line)



#def process_line(line):
    #line = re.sub(' +', ' ', line).strip()

    #logger.info(line)


if __name__ == '__main__':
    parse(sys.argv[1])
