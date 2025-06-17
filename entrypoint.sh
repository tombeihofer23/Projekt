#!/bin/bash
set -e

if [ "$LOAD_DATA" = "true" ] || [ ! -f "data/frankfurt.db" ]; then
  echo "Daten werden geladen (explizit oder erstmaliger Start)..."
  python initialize.py
else
  echo "Datenbank vorhanden – Initialisierung wird übersprungen."
fi

uv run start.py