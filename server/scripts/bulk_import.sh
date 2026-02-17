#!/bin/bash

# Simple wrapper script for bulk import
# Usage: ./run_bulk_import.sh /path/to/avatars [batch_size]

SOURCE_DIR="$1"
BATCH_SIZE="${2:-1000}"

if [ -z "$SOURCE_DIR" ]; then
    echo "Usage: $0 <source_directory> [batch_size]"
    echo "Example: $0 /opt/avatars 1000"
    exit 1
fi

echo "🎮 Starting Avatar Bulk Import"
echo "=============================="
echo "Source: $SOURCE_DIR"
echo "Batch Size: $BATCH_SIZE"
echo ""

# Run the import
python3 bulk_import_standalone.py "$SOURCE_DIR" --batch-size "$BATCH_SIZE" --skip-existing

echo ""
echo "✅ Bulk import completed!"
