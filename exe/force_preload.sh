#!/bin/bash

docker compose run --rm --profile route23 -e REPRELOAD=true app > ./logs/route23_preload.log 2>&1 &
