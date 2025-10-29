# -*- coding: utf-8 -*-

from odoo import models, fields


class ResConfigSettings(models.Model):
    _inherit = "res.company"

    custody_payment_journal_id = fields.Many2one("account.journal", string="Custody Payment Journal")
