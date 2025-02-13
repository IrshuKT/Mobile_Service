from odoo import fields, models
from odoo.api import model


class Brand(models.Model):
    _name = 'mobile.brand'
    _description = 'Mobile Brand'

    name = fields.Char(string='Mobile Brand')


class Model(models.Model):
    _name = 'mobile.model'
    _description = 'Mobile Model'
    _rec_name = 'model_name'

    brand_name = fields.Many2one('mobile.brand','Brand Name' ,required=True)
    model_name = fields.Char('Model Name',required=True)
    image = fields.Binary(string='Product Image')
