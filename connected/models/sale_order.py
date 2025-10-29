from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    branch_id = fields.Many2one('res.branch', string='Branch')

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    branch_id = fields.Many2one('res.branch', string='Branch')