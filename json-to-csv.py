#!/usr/bin/env python

import json
import csv
import os
import re
import sys

state_cli = sys.argv[1]

if not os.path.exists('csvs/'):
    os.makedirs('csvs/')

states_abbr = {
                'AK':'ALASKA',
                'AL':'ALABAMA',
                'AR':'ARKANSAS',
                'AZ':'ARIZONA',
                'CA':'CALIFORNIA',
                'CO':'COLORADO',
                'CT':'CONNECTICUT',
                'CZ':'CANAL ZONE',
                'DC':'WASHINGTON D.C.',
                'DE':'DELAWARE',
                'FL':'FLORIDA',
                'GA':'GEORGIA',
                'GMT':'GUAM',
                'HI':'HAWAII',
                'IA':'IOWA',
                'ID':'IDAHO',
                'IL':'ILLINOIS',
                'IN':'INDIANA',
                'KS':'KANSAS',
                'KY':'KENTUCKY',
                'LA':'LOUISIANA',
                'MA':'MASSACHUSETTS',
                'MD':'MARYLAND',
                'ME':'MAINE',
                'MI':'MICHIGAN',
                'MN':'MINNESOTA',
                'MO':'MISSOURI',
                'MS':'MISSIPPI',
                'MT':'MONTANA',
                'NB':'NEBRASKA',
                'NC':'NORTH CAROLINA',
                'ND':'NORTH DAKOTA',
                'NH':'NEW HAMPSHIRE',
                'NJ':'NEW JERSEY',
                'NM':'NEW MEXICO',
                'NV':'NEVADA',
                'NY':'NEW YORK',
                'OH':'OHIO',
                'OK':'OKLAHOMA',
                'OR':'OREGON',
                'PA':'PENNSYLVANIA',
                'PR':'PUERTO RICO',
                'RI':'RHODE ISLAND',
                'SC':'SOUTH CAROLINA',
                'SD':'SOUTH DAKOTA',
                'TN':'TENNESSEE',
                'TX':'TEXAS',
                'UT':'UTAH',
                'VA':'VIRGINIA',
                'VT':'VERMONT',
                'WA':'WASHINGTON',
                'WI':'WISCONSIN',
                'WV':'WEST VIRGINIA',
                'WY':'WYOMING'
              }

crimes =    [  'violent',
                'property',
                'murder',
                'robbery',
                'agg_assault',
                'burglary',
                'larceny_theft',
                'mvt',
                'arson'      
            ]

years = ['2011', '2012', '2013']

cats =   [  'mos',
            'count',
            'cleared',
            'cleared_pct'
        ]

csv_head =  [   'agency_type',
                'agency',
                'ori7',
                'state'
            ]

state = ''

for k, v in states_abbr.iteritems():
    if state_cli.upper() == v:
        state = k

for crime in crimes:
    for year in years:
        for cat in cats:
            csv_head.append(crime + "_" + year + "_" + cat)


csv_out = csv.writer(open("csvs/" + state + "_csv.csv", "wb+")) 

csv_out.writerow(csv_head)

files = [f for f in os.listdir('output/') if re.match(state + r".+\.json" , f)]

for file_ in files:
    line = []
    data = json.loads(open('output/' + file_).read())
    print("file:" + file_)
    line.append(data["agency_type"])
    line.append(data.get('agency', ''))
    line.append(data.get('ori7', ''))
    line.append(data.get('state', ''))
    for crime in crimes:
        for year in years:
            for cat in cats:
                line.append(data.get('crimes', {},).get(crime, {}).get(year, {}).get(cat))

    csv_out.writerow(line)
    line = []
    print("\n")

