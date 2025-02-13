from odoo import models,fields,api
from odoo.exceptions import UserError


class ProductIds(models.Model):
    _name = 'mobile.productids'
    _description = 'Getting Product to Service request'
   

    name  = fields.Many2one('product.product','Product', domain="[('categ_id.parent_id.name', '=', 'Mobile Accessories')]")
    used_quantity = fields.Integer(string='Qty')
    unit_price = fields.Float(string='Unit Price')
    stock_available = fields.Integer(string='On Hand')
    invoice_qty = fields.Integer(string='Invoiced Quantity')
    price = fields.Float(string='Price')
    grand_total = fields.Float(string="Grand Total", compute='_compute_grand_total')

    contact_id = fields.Many2one('mobile.contact')

    @api.onchange('name')
    def _onchange_name(self):
        if self.name:
                self.unit_price = self.name.list_price
                self.stock_available = self.name.qty_available

                if self.name.categ_id.parent_id.name != 'Mobile Accessories':
                    raise UserError("Products in the Mobile Accessories category cannot be selected.")


    @api.onchange('unit_price', 'used_quantity')
    def _compute_price(self):
        if self.unit_price and self.used_quantity:
            self.price = self.unit_price * self.used_quantity
        else:
            self.price = 0.0

    @api.depends('price')
    def _compute_grand_total(self):
        for record in self:
            # total = 0
            # for product in record.product_ids:
            #     #print(f"Product: {product.name}, Price: {product.price}, Quantity: {product.used_quantity}")
            #     total += product.unit_price * product.used_quantity
            record.grand_total = sum(product.unit_price for product in record.product_ids)

    def _get_on_hand_stock(self, name):
        """Fetch the on-hand stock for the given product."""
        # Get the available stock for the product
        stock_quant = self.env['stock.quant'].search([
            ('product_id', '=', name.id),
            ('quantity', '>', 0)  # Only count positive stock (available stock)
        ])

        # Return the total quantity of the product across all locations
        total_quantity = sum(quant.quantity for quant in stock_quant)
        return total_quantity

    def update_stock_availability(self):
        """Update stock availability manually."""
        for record in self:
            if record.name:
                # Get the on-hand stock and update the stock_moved field
                record.stock_available = self._get_on_hand_stock(record.name)