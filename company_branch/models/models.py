# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CompanyBranch(models.Model):
    _name = 'company.branch'
    _description = 'company Branch'

    user_id = fields.One2many('res.partner', 'branch_id')
    # branch_id = fields.Many2many('res.company', string='Branch', default=lambda self: self.env.company)
    branch_name = fields.Char(string='Branch')
    sale_order_ids =fields.One2many('sale.order', 'sale_branch_id')
    invoice_ids =fields.One2many('account.move', 'invoice_branch_id')


class SaleOrderInherited(models.Model):
    _inherit = 'sale.order'
    sale_branch_id = fields.Many2one('company.branch')


class AccountMoveInherited(models.Model):
    _inherit = 'account.move'
    invoice_branch_id = fields.Many2one('company.branch')

class ResPartnerInherited(models.Model):
    _inherit = 'res.partner'

    branch_id = fields.Many2one('company.branch')


