
#!/bin/sh
set -e

python init_production_db.py

exec gunicorn app:app --bind 0.0.0.0:${PORT:-10000}
