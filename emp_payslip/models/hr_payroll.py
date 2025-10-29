# -*- coding: utf-8 -*-
import base64
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import qrcode
from io import BytesIO
from odoo.tools import float_compare, float_is_zero


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    residency_num = fields.Char(string="Residency Number", required=False, )
    residency_date = fields.Date(string="Residency Expiration Date", required=False, )

    passport_num = fields.Char(string="Passport Number ", required=False, )
    passport_date = fields.Date(string="Passport Expiration Date", required=False, )

    license_num = fields.Char(string="Driving License Number", required=False, )
    license_date = fields.Date(string="License Expiration Date", required=False, )

    account_journal_id = fields.Many2one(comodel_name="account.journal", string="Payment Method")



