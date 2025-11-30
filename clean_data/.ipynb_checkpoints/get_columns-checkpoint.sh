#!/bin/bash

# Directory containing the CSV files
DIR="./"   # change if needed

echo "=== COLUMN NAMES FROM CSV FILES ==="

for file in "$DIR"/*.csv; do
    if [[ -f "$file" ]]; then
        echo
        echo "File: $(basename "$file")"
        # Print only the first line (header)
        head -n 1 "$file"
    fi
done
