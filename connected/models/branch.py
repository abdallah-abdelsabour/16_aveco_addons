# -*- coding: utf-8 -*-

from odoo import models, fields

class Branch(models.Model):
    _name = 'res.branch'
    _description = 'Branch Model'

    name = fields.Char(string='Branch Name', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True)


class InheritResUsrs(models.Model):
    _inherit = 'res.users'
    _description = 'Branch Model'

    branch_ids=fields.Many2many('res.branch')