# - * - coding: utf - 8 - * -
from email.policy import default

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.http import request
import requests
import logging

_logger = logging.getLogger(__name__)


class MobileService(models.Model):
    _name = 'mobile.contact'
    _description = 'Customer Details'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    #in_warranty = fields.Boolean('In Warranty', required=True, tracking=True)
    #repair = fields.Boolean('Repair', tracking=True)
    select_service = fields.Selection([
        ('in_warranty','In Warranty'),('repair','Repair')
    ],string='Service Mode',required = True,tracking=True)
    sequence = fields.Char(string='Service Number', required=True, copy=False, index=True, readonly=True,
                           default='New')
    name = fields.Many2one('res.partner', string='Customer Name', required=True, tracking=True)
    contact = fields.Char(string='Contact Number')
    email = fields.Char(string='Email')
    street = fields.Char(string='Address')
    street2 = fields.Char(string='Street2')
    city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state', string='State')
    zip = fields.Char(string='Zip')
    country_id = fields.Many2one('res.country', string='Country')
    active = fields.Boolean(default=True)

    brand_name = fields.Many2one('product.product', string='Mobile', required=True, tracking=True,
                                 domain=[ '|',
                                     ('categ_id.parent_id.name', '=', 'Mobile Phone'),('categ_id.name', '=', 'Mobile Phone')])

    request_date = fields.Date(default=fields.Date.today, string='Requested Date')
    return_date = fields.Date('Return Date')

    technician_id = fields.Many2one('res.users', 'Technician',domain="[('is_technician', '=', True)]")

    imei = fields.Char(string='IMEI Number')
    internal_notes = fields.Text(string='Internal Notes')

    service_ids = fields.One2many('mobile.complaint', 'contact_id')
    product_ids = fields.One2many('mobile.productids', 'contact_id')
    document_ids = fields.One2many('document.upload','contact_id')
    grand_total = fields.Float(string="Grand Total", compute='_compute_grand_total')

    invoice_id = fields.Many2one('account.move', string='Invoice',copy=False)
    invoice_count = fields.Integer(string="Invoice Count", compute='_compute_invoice_count')

    status = fields.Selection([('draft', 'Draft'), ('assigned', 'Assigned'), ('in_progress', 'In Progress'),
                               ('returned', 'Returned'), ('completed', 'Completed'), ],
                              default='draft')

    latitude = fields.Float(string='Latitude')
    longitude = fields.Float(string='Longitude')
    location = fields.Char(string='Location', compute='_compute_location', store=True)

    def generate_invoice(self):
        if self.invoice_id:
            raise UserError("An invoice already exists for this service request.")
        _logger.info("Generate Invoice button clicked!")  # Debugging
        # Ensure there are products to invoice
        if not self.product_ids:
            raise UserError("No products to invoice.")

        _logger.info(f"Products to invoice: {self.product_ids}")  # Debugging
        # Find the appropriate journal for the invoice
        journal = self.env['account.journal'].search([('type', '=', 'sale'), ('company_id', '=', self.env.company.id)],
                                                     limit=1)
        if not journal:
            raise UserError("No sales journal found for the company.")

        _logger.info(f"Journal found: {journal.name}")  # Debugging
        # Prepare the invoice values
        invoice_vals = {
            'move_type': 'out_invoice',  # Customer Invoice
            'partner_id': self.name.id,  # Customer (res.partner)
            'journal_id': journal.id,  # Use the correct sales journal
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [],
        }

        # Add products to the invoice
        for product in self.product_ids:
            invoice_vals['invoice_line_ids'].append((0, 0, {
                'product_id': product.name.id,
                'quantity': product.used_quantity,
                'price_unit': product.unit_price,
                'name': product.name.name,  # Product name
                'tax_ids': [(5, 0, 0)],  # Remove all taxes
            }))

        _logger.info(f"Invoice values: {invoice_vals}")  # Debugging
        # Create the invoice
        invoice = self.env['account.move'].create(invoice_vals)

        _logger.info(f"Invoice created: {invoice.name}")  # Debugging
        # Link the invoice back to the service
        self.invoice_id = invoice.id

        _logger.info("Invoice generation completed successfully!")  # Debugging
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _compute_invoice_count(self):
        for record in self:
            record.invoice_count = self.env['account.move'].search_count([('id', '=', record.invoice_id.id)])

    def action_view_invoice(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': self.invoice_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    """
    payment_status = fields.Selection(
        [('not_paid', 'Not Paid'), ('paid', 'Paid'), ('in_payment', 'Partially Paid')],
        string='Payment Status',
        compute='_compute_payment_status',
        store=True,
    )

    @api.depends('invoice_id.payment_state')
    def _compute_payment_status(self):
        for record in self:
            if record.invoice_id:
                # If the invoice is paid
                if record.invoice_id.payment_state == 'paid':
                    record.payment_status = 'paid'
                # If the invoice is partially paid
                elif record.invoice_id.payment_state == 'in_payment' or record.invoice_id.payment_state == 'partially_paid':
                    record.payment_status = 'partial'
                else:
                    record.payment_status = 'not_paid'
            else:
                record.payment_status = 'not_paid'
                """
    payment_status = fields.Char(string="Payment Status", compute='_compute_payment_status', store=True)

    @api.depends('invoice_id.payment_state')
    def _compute_payment_status(self):
        for record in self:
            if record.invoice_id:
                record.payment_status = record.invoice_id.payment_state
            else:
                record.payment_status = False




    # generating sequence
    @api.model
    def create(self, vals):
        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('service.memo') or 'New'
        return super(MobileService, self).create(vals)

    @api.depends('product_ids.price')
    def _compute_grand_total(self):
        for record in self:
            record.grand_total = sum(product.unit_price for product in record.product_ids)

    # picking details as per customer
    @api.onchange('name')
    def _onchange_name(self):
        if self.name:
            self.contact = self.name.phone
            self.email = self.name.email
            self.street = self.name.street
            self.street2 = self.name.street2
            self.city = self.name.city
            self.state_id = self.name.state_id
            self.zip = self.name.zip
            self.country_id = self.name.country_id
        else:
            self.contact = ''
            self.email = ''
            self.street = ''
            self.street2 = ''
            self.city = ''
            self.state_id = ''
            self.zip = ''
            self.country_id = ''

    def action_assign(self, args=None):
        self.status = 'assigned'

    def action_in_progress(self):
        self.status = 'in_progress'

    def action_completed(self):
        self.status = 'completed'

    def action_returned(self):
        self.status = 'returned'

    def action_print(self, args=None):
        return self.env.ref('mobileservice.report_service_ticket_action').report_action(self)

    # assigning technicians for work
    @api.depends('technician_id')
    def _compute_is_assigned_technician(self):
        for record in self:
            record.is_assigned_technician = (
                    record.technician_id.user_id.id == self.env.user.id) if record.technician_id else False

    @api.depends('latitude', 'longitude')
    def _compute_location(self):
        for record in self:
            if record.latitude and record.longitude:
                api_key = 'AIzaSyDRujuRJ-lqNDATgGDODZgrHRT6Q0v8mgQ'  # Replace with your actual API key
                try:
                    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={record.latitude},{record.longitude}&key={api_key}"
                    response = requests.get(url)
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('results'):
                            record.location = result['results'][0].get('formatted_address', 'Unknown Location')
                        else:
                            record.location = 'Unknown Location'
                    else:
                        record.location = 'Error fetching location'
                except Exception as e:
                    record.location = f"Error: {str(e)}"
            else:
                record.location = 'No location'

    @api.onchange(latitude, longitude)
    def _onchange_coordinates(self):
        if self.latitude and self.longitude:
            try:
                api_key = 'AIzaSyDRujuRJ-lqNDATgGDODZgrHRT6Q0v8mgQ'  # Replace with your API key
                url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={self.latitude},{self.longitude}&key={api_key}"
                response = requests.get(url)
                if response.status_code == 200:
                    result = response.json()
                    if result.get('results'):
                        self.location = result['results'][0].get('formatted_address', 'Unknown Location')
                    else:
                        self.location = 'Unknown Location'
                else:
                    self.location = 'Error fetching location'
            except Exception as e:
                self.location = f"Error: {str(e)}"

    @api.model
    def get_location_from_coordinates(self, latitude, longitude):
        try:
            api_key = 'AIzaSyDRujuRJ-lqNDATgGDODZgrHRT6Q0v8mgQ'  # Replace with your API key
            url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={api_key}"
            response = requests.get(url)
            if response.status_code == 200:
                result = response.json()
                if result.get('results'):
                    return result['results'][0].get('formatted_address', 'Unknown Location')
            return 'Unknown Location'
        except Exception as e:
            return f"Error: {str(e)}"

    """
    # notification while assigning works
            @api.onchange('technician_id')
    def _onchange_technician_id(self):
        if self.technician_id:
            if self.technician_id.user_id.partner_id:
                self.message_subscribe(partner_ids=[self.technician_id.user_id.partner_id.id])

    
    
    
            #archiving completed requests
    @api.model
    def create(self, vals_list):
        # Custom logic to handle "completed" status
        service = super(MobileService, self).create(vals_list)
        if service.status == 'completed':
            service.active = False  # Automatically archive completed requests
        return service

    def write(self, vals):
        result = super(MobileService, self).write(vals)
        for record in self:
            if record.status == 'completed':
                record.active = False  # Automatically archive completed requests
        return result
    
    
            journal = self.env['account.journal'].search([('type', '=', 'sale'), ('company_id', '=', self.env.company.id)],
                                                         limit=1)

            if not journal:
                raise UserError("No sales journal found for the company.")

            # Prepare the invoice values
            invoice_vals = {
                'move_type': 'out_invoice',  # Customer Invoice
                'partner_id': self.name.id,  # Customer (res.partner)
                'journal_id': journal.id,  # Use the correct sales journal
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': [],
            }

            #Create an invoice based on the service (including parts and labor)

            # Create invoice
            invoice_vals = {
                'move_type': 'out_invoice',  # Customer Invoice
                'partner_id': self.name.id,  # Customer (res.partner)
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': [],
            }

            invoice = self.env['account.move'].create(invoice_vals)

            # Add parts (from product_ids)
            for product in self.product_ids:
                invoice.write({
                    'invoice_line_ids': [(0, 0, {
                        'product_id': product.name.id,
                        'quantity': product.used_quantity,
                        'price_unit': product.unit_price,
                        'name': product.name,
                    })]
                })

            self.invoice_id = invoice.id  # Link the created invoice back to the service
            return invoice

           
            @api.onchange('technician_id')
                def _onchange_technician_id(self):
                    if self.technician_id:
                        if not self.sequence or self.sequence == 'New':
                            # Generate sequence only when technician is assigned
                            self.sequence = self.env['ir.sequence'].next_by_code('customer.mobile') or 'New'
                    else:
                        self.sequence = 'New'  # Keep the default if no technician is assigned"""
