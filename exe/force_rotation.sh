#!/bin/bash

docker compose run --rm -e FORCE_ROTATION=true app > ./logs/route23_rotation.log 2>&1 &
