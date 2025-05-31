#!/bin/bash

echo "Starting TTSAI Backend..."

# Initialize database with migration
echo "Running database migration..."
python migrate_to_sqlite.py || echo "Migration completed with warnings (this is expected if data already exists)"

# Start the application
echo "Starting Flask application..."
python app.py 