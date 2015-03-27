#/bin/bash

cd output
../s3-parallel-put/s3-parallel-put --bucket=apps.npr.org --prefix=dailygraphics/graphics/lookup-clearance-rates/data/ --gzip --put=stupid --grant=public-read .
