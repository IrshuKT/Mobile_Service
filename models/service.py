from odoo import models, fields, api
from odoo.exceptions import UserError


class MobileCategory(models.Model):
    _name = 'mobile.category'
    _description = 'Mobile Category Details'
    _rec_name = 'category'

    category = fields.Char(string='Category', required=True)


class MobileComplaint(models.Model):
    _name = 'mobile.complaint'
    _description = 'Complaint Details'

    category = fields.Many2one('mobile.category', string='Category', required=True)
    complaint_description = fields.Text(string='Description')
    contact_id = fields.Many2one('mobile.contact')


class MobileUnit(models.Model):
    _name = 'mobile.unit'
    _description = 'Measure unit'

    name = fields.Char(string='Unit of Measure', required=True)


class MobileProduct(models.Model):
    _name = 'mobile.product'
    _description = 'Product Details'
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Integer(string='Stock on Hand')
    unit_measure = fields.Many2one('mobile.unit', string='Unit of Measure')
    unit_price = fields.Float(string='Unit Price')


class MobileTerms(models.Model):
    _name = 'mobile.terms'
    _description = 'Terms and Condition'

    terms = fields.Text(string='Terms and Conditions')
