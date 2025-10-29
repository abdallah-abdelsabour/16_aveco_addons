# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.model
    def auto_allocate_payment(self):
        # Find payments that are posted and unallocated
        payments = self.search([('state', '=', 'posted'), ('invoice_ids', '=', False)])

        for payment in payments:
            # Find the partner's oldest unpaid invoice by invoice date
            oldest_invoice = self.env['account.move'].search([
                ('partner_id', '=', payment.partner_id.id),
                ('state', '=', 'posted'),
                ('type', '=', 'out_invoice')],
                order='invoice_date asc', limit=1)

            # Allocate the payment to the oldest invoice
            if oldest_invoice:
                payment.write({'invoice_ids': [(4, oldest_invoice.id)]})

class AccountPaymentAutoAllocation(models.Model):
    _name = 'account.payment.auto.allocation'
    _description = 'Automated Action for Payment Allocation'

    def _action_auto_allocate_payment(self):
        payment_obj = self.env['account.payment']
        payments = payment_obj.search([('state', '=', 'posted'), ('invoice_ids', '=', False)])

        for payment in payments:
            oldest_invoice = self.env['account.move'].search([
                ('partner_id', '=', payment.partner_id.id),
                ('state', '=', 'posted'),
                ('type', '=', 'out_invoice')],
                order='invoice_date asc', limit=1)

            if oldest_invoice:
                payment.write({'invoice_ids': [(4, oldest_invoice.id)]})

    name = fields.Char('Name')
    trigger_model_id = fields.Many2one('ir.model', string='Trigger Model', required=True, domain=[('model', 'like', 'account.payment')])
    trigger_condition = fields.Char('Trigger Condition')
    trigger_on_create = fields.Boolean('On Creation')
    active = fields.Boolean(default=True)

    def run_action(self):
        self._action_auto_allocate_payment()

