from odoo import models,fields


class Technician(models.Model):
    _name = 'mobile.technician'
    _inherit = ['mail.thread']
    _description = 'Technician Details'

    name = fields.Char(string='Name',required =True)
    phone = fields.Char(string='Contact Number')
    role = fields.Char(string='Position')
    email = fields.Char(string='Email')
    address = fields.Text('Address')
    user_id = fields.Many2one('res.users',string='Related User',required=True)


class RESUSER(models.Model):
    _inherit = 'res.users'

    is_technician = fields.Boolean(string='Is Technician ?')