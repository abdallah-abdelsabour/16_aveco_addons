from odoo import fields, models, api,_
from num2words import num2words
from odoo.exceptions import UserError


class AccountPyment(models.Model):
    _inherit = 'account.payment'

    def action_post(self):
        res = super().action_post()
        for payment in self:
            if payment.analytic_distribution:
                for line in payment.move_id.line_ids:
                    # Apply analytic_distribution to all lines with accounts if not set
                    if not line.analytic_distribution:
                        line.analytic_distribution = payment.analytic_distribution
        return res
    accounts = fields.Many2one(
        'account.account',
        string='Accounts',
        required=False)

    amount_in_words_ar =fields.Char(string='Amount in Words', compute='_compute_amount_in_words')
    # amount_in_words_en =fields.Char(string='Amount in Words', compute='_compute_amount_in_words')
    check_number = fields.Char(string='Check Number',readonly=False,)
    due_date = fields.Date(string='Due Date')
    analytic_line_ids = fields.One2many(
        comodel_name='account.analytic.line', inverse_name='move_line_id',
        string='Analytic lines',)
    analytic_distribution = fields.Json(store=True, string="Analytic Distribution")
    analytic_precision = fields.Integer(
        store=False,
        default=lambda self: self.env['decimal.precision'].precision_get("Percentage Analytic"),)


    @api.depends('amount', 'journal_id')
    def _compute_amount_in_words(self):
        for record in self:
            if record.journal_id.type in ['bank', 'cash']:
                whole_part = int(record.amount)
                fractional_part = round(record.amount - whole_part, 2)
                whole_in_words = num2words(whole_part, to='cardinal', lang='ar')
                # whole_in_words_en = num2words(whole_part, to='cardinal', lang='en')
                if fractional_part > 0:
                    fractional_in_words = num2words(int(fractional_part * 100), to='cardinal', lang='ar')
                    # fractional_in_words_en = num2words(int(fractional_part * 100), to='cardinal', lang='en')
                    record.amount_in_words_ar = f"{whole_in_words}  جنيهاً و {fractional_in_words} قرشًا"
                    # record.amount_in_words_en = f"{whole_in_words_en} Pounds and {fractional_in_words_en} Piasters"
                else:
                    record.amount_in_words_ar =f"{whole_in_words} جنيها  ً"
                    # record.amount_in_words_en =f"{whole_in_words_en} Pounds"
            else:
                record.amount_in_words_ar = ''
                # record.amount_in_words_en = ''

    def _seek_for_lines(self):
        ''' Helper used to dispatch the journal items between:
        - The lines using the temporary liquidity account.
        - The lines using the counterpart account.
        - The lines being the write-off lines.
        :return: (liquidity_lines, counterpart_lines, writeoff_lines)
        '''
        self.ensure_one()

        liquidity_lines = self.env['account.move.line']
        counterpart_lines = self.env['account.move.line']
        writeoff_lines = self.env['account.move.line']

        for line in self.move_id.line_ids:
            if line.account_id in self._get_valid_liquidity_accounts():
                liquidity_lines += line
            elif line.account_id.account_type in ('asset_receivable', 'liability_payable') or line.partner_id == line.company_id.partner_id or line.account_id ==self.accounts:
                counterpart_lines += line
            else:
                writeoff_lines += line

        return liquidity_lines, counterpart_lines, writeoff_lines

    @api.depends('journal_id', 'partner_id', 'partner_type', 'is_internal_transfer', 'destination_journal_id' ,'accounts')
    def _compute_destination_account_id(self):
        self.destination_account_id = False
        for pay in self:
            if pay.is_internal_transfer:
                pay.destination_account_id = pay.destination_journal_id.company_id.transfer_account_id
            elif pay.partner_type == 'customer':
                # Receive money from invoice or send money to refund it.
                if pay.partner_id:
                    pay.destination_account_id = pay.accounts.id or pay.partner_id.with_company(
                        pay.company_id).property_account_receivable_id
                else:
                    pay.destination_account_id = self.env['account.account'].search([
                        ('company_id', '=', pay.company_id.id),
                        ('account_type', '=', 'asset_receivable'),
                        ('deprecated', '=', False),
                    ], limit=1)
                if pay.accounts:
                    pay.destination_account_id = pay.accounts.id

            elif pay.partner_type == 'supplier':
                # Send money to pay a bill or receive money to refund it.
                if pay.partner_id:
                    pay.destination_account_id = pay.accounts.id or pay.partner_id.with_company(
                        pay.company_id).property_account_payable_id
                else:
                    pay.destination_account_id = self.env['account.account'].search([
                        ('company_id', '=', pay.company_id.id),
                        ('account_type', '=', 'liability_payable'),
                        ('deprecated', '=', False),
                    ], limit=1)
                if pay.accounts:
                    pay.destination_account_id = pay.accounts.id

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        ''' Prepare the dictionary to create the default account.move.lines for the current payment.
        :param write_off_line_vals: Optional list of dictionaries to create a write-off account.move.line easily containing:
            * amount:       The amount to be added to the counterpart amount.
            * name:         The label to set on the line.
            * account_id:   The account on which create the write-off.
        :return: A list of python dictionary to be passed to the account.move.line's 'create' method.
        '''
        self.ensure_one()
        write_off_line_vals = write_off_line_vals or {}

        if not self.outstanding_account_id:
            raise UserError(_(
                "You can't create a new payment without an outstanding payments/receipts account set either on the company or the %s payment method in the %s journal.",
                self.payment_method_line_id.name, self.journal_id.display_name))

        # Compute amounts.
        write_off_line_vals_list = write_off_line_vals or []
        write_off_amount_currency = sum(x['amount_currency'] for x in write_off_line_vals_list)
        write_off_balance = sum(x['balance'] for x in write_off_line_vals_list)
        credit_analytic_distribution = False
        debit_analytic_distribution = False
        if self.payment_type == 'inbound': #receive
            credit_analytic_distribution = self.analytic_distribution
            liquidity_amount_currency = self.amount
        elif self.payment_type == 'outbound':   #send
            debit_analytic_distribution = self.analytic_distribution
            liquidity_amount_currency = -self.amount
        else:
            liquidity_amount_currency = 0.0

        liquidity_balance = self.currency_id._convert(
            liquidity_amount_currency,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        counterpart_amount_currency = -liquidity_amount_currency - write_off_amount_currency
        counterpart_balance = -liquidity_balance - write_off_balance
        currency_id = self.currency_id.id

        # Compute a default label to set on the journal items.
        liquidity_line_name = ''.join(x[1] for x in self._get_liquidity_aml_display_name_list())
        counterpart_line_name = ''.join(x[1] for x in self._get_counterpart_aml_display_name_list())
        line_vals_list = [
            # Liquidity line.
            {
                'name': liquidity_line_name,
                'date_maturity': self.date,
                'amount_currency': liquidity_amount_currency,
                'currency_id': currency_id,
                'debit': liquidity_balance if liquidity_balance > 0.0 else 0.0,
                'credit': -liquidity_balance if liquidity_balance < 0.0 else 0.0,
                'analytic_distribution': debit_analytic_distribution if self.payment_type == 'inbound' else credit_analytic_distribution,
                'partner_id': self.partner_id.id,
                'account_id': self.outstanding_account_id.id,
            },
            # Receivable / Payable.
            {
                'name': counterpart_line_name,
                'date_maturity': self.date,
                'amount_currency': counterpart_amount_currency,
                'currency_id': currency_id,
                'debit': counterpart_balance if counterpart_balance > 0.0 else 0.0,
                'credit': -counterpart_balance if counterpart_balance < 0.0 else 0.0,
                'analytic_distribution': credit_analytic_distribution if self.payment_type == 'inbound' else debit_analytic_distribution,
                'partner_id': self.partner_id.id,
                'account_id':self.destination_account_id.id,
            },
        ]
        
        return line_vals_list + write_off_line_vals_list 
