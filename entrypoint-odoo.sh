#!/bin/bash
set -e

echo "🚀 Waiting for database to be ready..."
while ! pg_isready -h db -p 5432 -U odoo; do sleep 1; done
echo "✅ Database is ready!"

echo "🔄 Updating Odoo module hiscox_integration..."
odoo -d odoo --update hiscox_integration --stop-after-init

echo "🚀 Starting Odoo..."
exec /entrypoint.sh odoo
