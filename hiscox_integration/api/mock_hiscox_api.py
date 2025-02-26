from flask import Flask, request, jsonify
import psycopg2
import os
import time

app = Flask(__name__)

# PostgreSQL Connection Config
DB_NAME = os.getenv("POSTGRES_DB", "odoo")
DB_USER = os.getenv("POSTGRES_USER", "odoo")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "odoo")
DB_HOST = os.getenv("DB_HOST", "db")  # db is the service name in docker-compose
DB_PORT = os.getenv("DB_PORT", "5432")


def get_db_connection():
    """Establish database connection with retry logic"""
    retries = 5
    while retries > 0:
        try:
            print(f"Trying to connect to PostgreSQL at {DB_HOST}:{DB_PORT} with user {DB_USER}")
            conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
            )
            print(" Database connection successful!")
            return conn
        except Exception as e:
            print(f"Database connection failed: {str(e)}. Retrying in 3s...")
            time.sleep(3)
            retries -= 1
    raise Exception("Unable to connect to the database after multiple retries.")


@app.route('/submit', methods=['POST'])
def submit():
    """Receives application data and stores it in PostgreSQL"""
    data = request.json
    email = data.get("email")
    name = data.get("name")
    phone = data.get("phone")

    if not email or not name or not phone:
        return jsonify({"error": "Missing required fields (name, email, phone)"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        print(f" Inserting data: Name={name}, Email={email}, Phone={phone}")

        try:
            cur.execute("""
                        INSERT INTO edited_hiscox_case (name, email, phone, application_status)
                        VALUES (%s, %s, %s, 'submitted')
                        ON CONFLICT (email) DO UPDATE 
                        SET name = EXCLUDED.name, 
                        phone = EXCLUDED.phone, 
                        application_status = 'submitted';
                    """, (name, email, phone))
        except Exception as db_error:
            print(f" DATABASE ERROR: {db_error}")
            conn.rollback()
            return jsonify({"error": f"Database error: {str(db_error)}"}), 500

        conn.commit()
        cur.close()
        conn.close()

        print("Data successfully submitted to PostgreSQL")
        return jsonify({"message": "Application submitted"}), 200

    except Exception as e:
        print(f" UNEXPECTED ERROR: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/status', methods=['GET'])
def status():
    """Fetches the current application status from PostgreSQL"""
    email = request.args.get("email")

    if not email:
        return jsonify({"error": "Email parameter is required"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT application_status FROM edited_hiscox_case WHERE email = %s", (email,))
        result = cur.fetchone()

        cur.close()
        conn.close()

        if result:
            print(f" Status found: {result[0]}")
            return jsonify({"status": result[0]}), 200
        else:
            print(" No status found for this email")
            return jsonify({"status": "not found"}), 404

    except Exception as e:
        print(f"Error fetching status from PostgreSQL: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
