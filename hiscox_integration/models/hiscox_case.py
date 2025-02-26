import base64
import logging
import time
from io import BytesIO
import qrcode
import requests
from psycopg2 import OperationalError
from odoo import models, fields

_logger = logging.getLogger(__name__)

HISCOX_API_URL = "http://hiscox_mock_api:5000"  # Use service name instead of IP


class HiscoxCase(models.Model):
    _name = 'edited.hiscox.case'
    _description = 'Hiscox Insurance Case'

    name = fields.Char(string="Customer Name", required=True)
    email = fields.Char(string="Email", required=True)
    phone = fields.Char(string="Phone", required=True)
    application_status = fields.Selection([
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string="Application Status", default='pending')

    qr_code = fields.Binary(string="QR Code", readonly=True)
    submitted = fields.Boolean(string="Submitted", default=False)

    def generate_qr_code(self):
        """Generates a QR Code and stores it as a base64-encoded image."""
        for record in self:
            qr_data = f"Name: {record.name}\nEmail: {record.email}\nPhone: {record.phone}\nStatus: {record.application_status}"
            qr = qrcode.QRCode(
                version=1,  # Control QR complexity (1 = Smallest, up to 40)
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=2,  # Controls how large each QR box is
                border=1  # Removes extra white space
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            img = qr.make_image(fill="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            record.qr_code = base64.b64encode(buffer.getvalue())  # Store as binary

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'QR Code Generated',
                'type': 'success',
                'sticky': False
            },
        }

    def submit_to_hiscox(self):
        """Submits application data to Hiscox Mock API with serialization handling"""
        headers = {"Content-Type": "application/json"}

        for record in self:

            #Step 1: Check existing status via GET request
            try:
                response = requests.get(f"{HISCOX_API_URL}/status?email={record.email}", headers=headers)
                response.raise_for_status()
                status = response.json().get("status")

                if status == "submitted":
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': 'Warning',
                            'message': 'Already Submitted!!!',
                            'type': 'warning',
                            'sticky': False
                        }
                    }
            except requests.exceptions.RequestException as e:
                _logger.error(f"Failed to check status for {record.email}: {str(e)}")

                #Step 2: Proceed with submission via POST request
            data = {
                "name": record.name,
                "email": record.email,
                "phone": record.phone,
                "status": record.application_status
            }

            try:
                response = requests.post(f"{HISCOX_API_URL}/submit", json=data, headers=headers)
                response.raise_for_status()

                #Fix Transaction Error: Use Manual Commit & Rollback
                max_retries = 5
                for attempt in range(1, max_retries + 1):
                    try:
                        self.env.cr.execute("BEGIN;")  # Start transaction

                        #Lock the row to prevent concurrency issues
                        self.env.cr.execute("""
                                        SELECT id FROM edited_hiscox_case WHERE id = %s FOR UPDATE NOWAIT
                                    """, (record.id,))

                        record.with_company(self.env.company).write({
                            'application_status': 'submitted',
                            'submitted': True
                        })

                        self.env.cr.execute("COMMIT;")  #Commit transaction if successful
                        _logger.info(f"Successfully submitted application for {record.email}")
                        break

                    except OperationalError as db_error:
                        self.env.cr.execute("ROLLBACK;")  #Rollback transaction on failure

                        if "could not serialize access due to concurrent update" in str(db_error):
                            _logger.warning(f"Serialization failure, retrying ({attempt}/{max_retries})...")
                            time.sleep(0.5 * attempt)  # Incremental backoff
                        else:
                            _logger.error(f"Database write failed: {str(db_error)}")
                            raise  # Rethrow if it's not a serialization issue

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success',
                        'message': 'Your application has been submitted successfully!',
                        'type': 'success',
                        'sticky': False
                    }
                }

            except requests.exceptions.RequestException as e:
                _logger.error(f"Hiscox API submission failed for {record.email}: {str(e)}")

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Error',
                'message': 'Submission failed. Please try again!',
                'type': 'danger',
                'sticky': False
            }
        }

    def check_status_from_hiscox(self):
        """Fetches the application status from Hiscox Mock API"""
        for record in self:
            try:
                response = requests.get(f"{HISCOX_API_URL}/status?email={record.email}")
                print(response)
                response.raise_for_status()
                status = response.json().get("status")
                if status:
                    record.application_status = status
                    _logger.info(f"Updated application status to: {record.application_status}")
            except requests.exceptions.RequestException as e:
                _logger.error(f"Hiscox API status check failed: {str(e)}")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Application Status',
                'message': f"Current Status: {record.application_status}",
                'type': 'info',
                'sticky': False
            }
        }
