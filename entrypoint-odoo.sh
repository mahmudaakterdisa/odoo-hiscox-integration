#!/bin/bash
set -e

echo "Waiting for database to be ready..."
while ! pg_isready -h db -p 5432 -U odoo; do sleep 1; done
echo "Database is ready!"

export PGPASSWORD="odoo"  # Set PostgreSQL password for authentication

echo "Updating Odoo module hiscox_integration..."
odoo -d odoo --update hiscox_integration --stop-after-init

echo "Checking if table 'edited_hiscox_case' exists..."
TABLE_EXISTS=$(psql -h db -U odoo -d odoo -tAc "SELECT to_regclass('public.edited_hiscox_case');")

if [ "$TABLE_EXISTS" != "edited_hiscox_case" ]; then
    echo "Table 'edited_hiscox_case' not found! Creating it now..."
    psql -h db -U odoo -d odoo -c "
    CREATE TABLE IF NOT EXISTS edited_hiscox_case (
        id SERIAL PRIMARY KEY,
        create_uid INTEGER,
        write_uid INTEGER,
        name VARCHAR NOT NULL,
        email VARCHAR NOT NULL,
        phone VARCHAR NOT NULL,
        application_status VARCHAR,
        submitted BOOLEAN,
        create_date TIMESTAMP,
        write_date TIMESTAMP
    );"
else
    echo "Table 'edited_hiscox_case' already exists."
fi

echo "Ensuring unique constraint on email column..."
psql -h db -U odoo -d odoo -c "
DO \$\$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE table_name = 'edited_hiscox_case'
        AND constraint_name = 'unique_email'
    ) THEN
        ALTER TABLE edited_hiscox_case ADD CONSTRAINT unique_email UNIQUE (email);
    END IF;
END \$\$;
"

unset PGPASSWORD  # Remove password variable for security

echo "Starting Odoo..."
exec /entrypoint.sh odoo
