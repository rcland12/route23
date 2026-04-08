#!/bin/bash

docker compose run --rm -e REPRELOAD=true app > ./logs/route23_preload.log 2>&1 &
