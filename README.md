# UCR Clearance Parser

The UCR Clearance Parser powers the NPR Visuals [crime clearance lookup tool](http://www.npr.org/2015/03/30/395799413/how-many-crimes-do-your-police-clear-now-you-can-find-out) by processing raw FBI UCR clearance data and generating an agency lookup file and JSON files for each law enforcement agency.

## Install

Requires PostgreSQL. See the [NPR Visuals guide](http://blog.apps.npr.org/2013/06/06/how-to-setup-a-developers-environment.html) to set up a Mac development environment with PostgreSQL.

```
pip install -r requirements.txt
git submodule update --init
```

## Process data

```
./process.sh
```

This generates approximately 22,000 JSON files of the form `<ori7>.json` (e.g. `NY03030.json`) and `agency_names.csv` in the `output` directory.

## Deploy

Requires AWS environment variables to be set.

```
./deploy.sh
```

## Notes

* Crosswalk file converted from Stata to CSV using R from [Law Enforcement Agency Identifiers Crosswalk, 2005](http://www.icpsr.umich.edu/icpsrweb/NACJD/studies/4634).
* The JSON writer -- `write_clearance_json()` in `parse.py` -- is quite ugly. If you need to extend the JSON output, consider refactoring this function. Pull requests encouraged!
* The `parse()` function `parse.py` is a handy, fast parser for raw FBI UCR clearance data files, known as "master" files.
* [`data/UCR52406-2013.txt`](data/UCR52406-2013.txt) is the FBI master agency list as exported from the UCR system. It was not used in our final product, but might be useful.
* The scripts and processed output contains median clearance rates based on population bucket. **These medians are technically correct but not necessarily reliable**. This is because there are many zeroes in the clearance data that bias the medians. The zeroes are ambiguous: they could be because the agency did not report, because their data was rejected by the FBI, or because they did no clear any cases. Use with care.

## License

MIT licensed, see [LICENSE](LICENSE) for details.
