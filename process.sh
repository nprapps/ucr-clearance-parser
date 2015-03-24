#/bin/bash

dropdb --if-exists ucr_clearance
createdb ucr_clearance
./parse.py
