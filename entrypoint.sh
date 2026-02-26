#!/bin/bash

# Exit on error
set -e

echo "🔄 Waiting for PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "✅ PostgreSQL is ready!"

echo "🔄 Waiting for Redis..."
while ! nc -z $REDIS_HOST $REDIS_PORT; do
  sleep 0.1
done
echo "✅ Redis is ready!"

echo "🔄 Running migrations..."
python manage.py migrate --noinput

echo "🔄 Collecting static files..."
python manage.py collectstatic --noinput

echo "🔄 Creating default categories..."
python manage.py create_default_categories

echo "✅ Setup complete!"

# Execute the main command
exec "$@"
```

---