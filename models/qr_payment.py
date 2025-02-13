from odoo import models,fields,api
import qrcode
from io import BytesIO
import base64


"""class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    upi_id = fields.Char(string="UPI ID", help="Enter the UPI ID for this bank account.")

class AccountSetupBankManualConfig(models.Model):
    _inherit = 'account.setup.bank.manual.config'

    upi_id = fields.Char(string="UPI ID", help="Enter the UPI ID for this bank account.")"""

class AccountInvoice(models.Model):
    _inherit = 'account.move'

    def generate_upi_url(self):
        """Generate UPI payment URL based on invoice details."""
        upi_id = "irshad2934@okhdfcbank"  # Replace with your UPI ID
        amount = self.amount_total
        invoice_number = self.name
        upi_url = f"upi://pay?pa={upi_id}&pn=IRSHAD KT&am={amount}&tn=Payment for Invoice {invoice_number}"
        return upi_url

    def generate_qr_code(self):
        """Generate QR code image and return it as base64."""
        upi_url = self.generate_upi_url()
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(upi_url)
        qr.make(fit=True)
        img = qr.make_image(fill='blue', back_color='white')

        # Convert image to base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()