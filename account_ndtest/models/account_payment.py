from odoo import fields, models, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_post(self):
        res = super().action_post()
        inv = self.env['account.move'].search(
            [('partner_id', '=', self.partner_id.id), ('payment_state', 'in', ('not_paid', 'partial')),
             ('move_type', '=', 'out_invoice')],
            order='create_date', limit=1)
        if inv:
            print(inv)
            payment_wizard=inv.action_register_payment()
            return payment_wizard
        return res
