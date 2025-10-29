# -*- coding: utf-8 -*-

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    custody_payment_journal_id = fields.Many2one(related="company_id.custody_payment_journal_id",
                                                 string="Custody Payment Journal", readonly=False)
