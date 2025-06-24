#!/bin/bash
set -e

if [ "$LOAD_DATA" = "true" ] ; then
  python /app/init.py --with-historical
else
  python /app/init.py
fi

python /app/start.py