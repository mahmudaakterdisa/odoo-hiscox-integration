import base64
import qrcode
import requests
import logging
from io import BytesIO
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

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
    qr_code = fields.Binary(string="QR Code")

    @api.model
    def create_qr_code(self):
        """Generates a QR Code for the application containing all customer data"""
        qr_data = f"Name: {self.name}\nEmail: {self.email}\nPhone: {self.phone}\nStatus: {self.application_status}"
        qr = qrcode.make(qr_data)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        self.qr_code = base64.b64encode(buffer.getvalue())
        return True

    def submit_to_hiscox(self):
        """Submits application data to Hiscox Mock API"""
        hiscox_api_url = "http://localhost:5000/submit"
        headers = {"Content-Type": "application/json"}
        data = {
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "status": self.application_status
        }
        try:
            response = requests.post(hiscox_api_url, json=data, headers=headers)
            response.raise_for_status()
            self.application_status = 'submitted'
        except requests.exceptions.RequestException as e:
            _logger.error(f"Hiscox API submission failed: {str(e)}")

    def check_status_from_hiscox(self):
        """Fetches the application status from Hiscox Mock API"""
        hiscox_api_url = "http://localhost:5000/status"
        try:
            response = requests.get(f"{hiscox_api_url}?email={self.email}")
            response.raise_for_status()
            status = response.json().get("status")
            if status:
                self.application_status = status
        except requests.exceptions.RequestException as e:
            _logger.error(f"Hiscox API status check failed: {str(e)}")
