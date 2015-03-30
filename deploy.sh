#/bin/bash

cd output
../s3-parallel-put/s3-parallel-put --bucket=apps.npr.org --prefix=dailygraphics/graphics/lookup-clearance-rates/json/ --gzip --header="Cache-control:max-age=20" --put=stupid --grant=public-read .
