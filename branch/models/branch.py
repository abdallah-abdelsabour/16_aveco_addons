from odoo import models, fields, api


class Branch(models.Model):
    _name = 'res.branch'

    name = fields.Char()
    company_id = fields.Many2one('res.company')
    order_ids = fields.One2many(comodel_name='sale.order', inverse_name='branch_id')
    move_ids = fields.One2many(comodel_name='account.move', inverse_name='branch_id')
    user_ids = fields.Many2many('res.users')


class ResUser(models.Model):
    _inherit = 'res.users'

    branch_ids = fields.Many2many('res.branch')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    branch_id = fields.Many2one('res.branch')


class AccountMove(models.Model):
    _inherit = 'account.move'

    branch_id = fields.Many2one('res.branch')
