# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountPaymentInherrited(models.Model):
    _inherit = 'account.payment'


    def action_post(self):
        res = super(AccountPaymentInherrited, self).action_post()
        inv = self.env['account.move'].search([('partner_id.id', '=', self.partner_id.id)])
        print(".....", inv)
        moves = []
        for move in inv:
            if move.payment_state in ('not_paid', 'partial'):
                moves.append(move)
        list_of_date = moves.mapped('invoice_date')
        oldest_date = min(list_of_date)

        for inv in moves:
            pass

            return res