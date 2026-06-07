#!/bin/bash

docker compose run --rm --profile route23 -e FORCE_ROTATION=true app > ./logs/route23_rotation.log 2>&1 &
