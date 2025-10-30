import io
import json
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class ExpenseReportWizard(models.TransientModel):
    _name = 'expense.report.wizard'
    _description = 'Expense Report Wizard'

    date_from = fields.Date(
        string='Date From',
        required=True,
        default=lambda self: fields.Date.today().replace(day=1)
    )
    date_to = fields.Date(
        string='Date To',
        required=True,
        default=fields.Date.today
    )

    state_filter = fields.Selection([
        ('all', 'All Entries'),
        ('posted', 'Posted Only'),
    ], string='Entry State', default='all', required=True)

    partner_ids = fields.Many2many(
        'res.partner',
        string='Customers',
        help='Leave empty to include all customers'
    )

    analytic_account_ids = fields.Many2many(
        'account.analytic.account',
        string='Analytic Accounts',
        help='Leave empty to include all analytic accounts. Selected accounts will become columns in the report.'
    )

    account_ids = fields.Many2many(
        'account.account',
        string='Accounts',
        help='Leave empty to include all accounts'
    )
    account_code_from = fields.Char(
        string='Account Code From',
        help='Filter accounts starting from this code'
    )
    account_code_to = fields.Char(
        string='Account Code To',
        help='Filter accounts up to this code'
    )
    account_group_id = fields.Many2one(
        'account.group',
        string='Account Group',
        help='Filter by account group'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    def _get_domain_filters(self):
        """Build domain for account.move.line query based on filters"""
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('company_id', '=', self.company_id.id),
        ]

        if self.state_filter == 'posted':
            domain.append(('move_id.state', '=', 'posted'))

        if self.partner_ids:
            domain.append(('partner_id', 'in', self.partner_ids.ids))

        if self.account_ids:
            domain.append(('account_id', 'in', self.account_ids.ids))

        if self.account_code_from:
            domain.append(('account_id.code', '>=', self.account_code_from))

        if self.account_code_to:
            domain.append(('account_id.code', '<=', self.account_code_to))

        if self.account_group_id:
            accounts = self.env['account.account'].search([
                ('group_id', 'child_of', self.account_group_id.id)
            ])
            if accounts:
                domain.append(('account_id', 'in', accounts.ids))

        return domain

    def _get_report_data(self):
        domain = self._get_domain_filters()

        move_lines = self.env['account.move.line'].search(domain, order='account_id')

        if not move_lines:
            raise UserError(_('No data found for the selected filters.'))

        if self.analytic_account_ids:
            analytic_accounts = self.analytic_account_ids
        else:
            analytic_ids = set()
            for line in move_lines:
                if line.analytic_distribution:
                    analytic_ids.update([int(k) for k in line.analytic_distribution.keys()])

            if analytic_ids:
                analytic_accounts = self.env['account.analytic.account'].browse(list(analytic_ids)).sorted(key=lambda a: a.name)
            else:
                analytic_accounts = self.env['account.analytic.account']

        accounts = move_lines.mapped('account_id').sorted(key=lambda a: a.code)

        data_matrix = {}
        for account in accounts:
            data_matrix[account.id] = {
                'account': account,
                'analytics': {}
            }
            for analytic in analytic_accounts:
                data_matrix[account.id]['analytics'][analytic.id] = 0.0
            if not self.analytic_account_ids or any(not line.analytic_distribution for line in move_lines if line.account_id.id == account.id):
                data_matrix[account.id]['analytics'][False] = 0.0

        for line in move_lines:
            account_id = line.account_id.id

            if account_id not in data_matrix:
                continue

            if line.analytic_distribution:
                for analytic_id_str, percentage in line.analytic_distribution.items():
                    analytic_id = int(analytic_id_str)
                    if analytic_id in data_matrix[account_id]['analytics']:
                        # Amount is distributed by percentage (usually 100.0)
                        distributed_amount = line.balance * (percentage / 100.0)
                        data_matrix[account_id]['analytics'][analytic_id] += distributed_amount
            else:
                if False in data_matrix[account_id]['analytics']:
                    data_matrix[account_id]['analytics'][False] += line.balance

        return {
            'data_matrix': data_matrix,
            'analytic_accounts': analytic_accounts,
            'accounts': accounts,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'company_name': self.company_id.name,
        }

    def generate_xlsx_report(self, data):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(_('Expense Report'))

        sheet.right_to_left()

        header_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#FFD700',
            'border': 1,
        })

        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })

        date_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })

        column_header_format = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D3D3D3',
            'border': 1,
            'text_wrap': True,
        })

        account_column_header_format = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D3D3D3',
            'border': 1,
            'text_wrap': True,
        })

        account_cell_format = workbook.add_format({
            'font_size': 10,
            'align': 'right',
            'valign': 'vcenter',
            'bg_color': '#D3D3D3',
            'border': 1,
        })

        cell_format = workbook.add_format({
            'font_size': 10,
            'align': 'right',
            'valign': 'vcenter',
            'border': 1,
        })

        number_format = workbook.add_format({
            'font_size': 10,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'num_format': '#,##0.00',
        })

        # Total row formats
        total_label_format = workbook.add_format({
            'bold': True,
            'font_size': 11,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#FFC000',
            'border': 2,
        })

        total_number_format = workbook.add_format({
            'bold': True,
            'font_size': 11,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#FFC000',
            'border': 2,
            'num_format': '#,##0.00',
        })

        data_matrix = data['data_matrix']
        analytic_accounts = data['analytic_accounts']
        accounts = data['accounts']

        has_no_analytic = any(False in account_data['analytics'] for account_data in data_matrix.values())

        column_list = list(analytic_accounts)
        if has_no_analytic:
            column_list.append(False)

        num_cols = len(column_list)
        total_cols = num_cols + 1

        sheet.merge_range(0, 0, 0, total_cols - 1, data['company_name'], header_format)
        sheet.set_row(0, 30)

        report_title = _('Expense Transactions Report')
        sheet.merge_range(1, 0, 1, total_cols - 1, report_title, title_format)
        sheet.set_row(1, 25)

        date_from_str = data['date_from'].strftime('%Y-%m-%d')
        date_to_str = data['date_to'].strftime('%Y-%m-%d')
        date_range = _('From %s To %s') % (date_from_str, date_to_str)
        sheet.merge_range(2, 0, 2, total_cols - 1, date_range, date_format)
        sheet.set_row(2, 25)

        row = 4
        col = 0

        sheet.write(row, col, _('Description'), account_column_header_format)
        sheet.set_column(col, col, 35)
        col += 1

        for item in column_list:
            if item:
                sheet.write(row, col, item.name, column_header_format)
            else:
                sheet.write(row, col, _('No Analytic'), column_header_format)
            sheet.set_column(col, col, 15)
            col += 1

        row = 5
        # Dictionary to store column totals
        column_totals = {item: 0.0 for item in column_list}

        for account_id, account_data in data_matrix.items():
            account = account_data['account']
            col = 0

            account_desc = f"[{account.code}] {account.name}"
            sheet.write(row, col, account_desc, account_cell_format)
            col += 1

            for item in column_list:
                analytic_id = item.id if item else False
                amount = account_data['analytics'].get(analytic_id, 0.0)
                sheet.write(row, col, amount, number_format)
                column_totals[item] += amount
                col += 1

            row += 1

        # Add total row
        col = 0
        sheet.write(row, col, _('Total'), total_label_format)
        col += 1

        for item in column_list:
            total_amount = column_totals[item]
            sheet.write(row, col, total_amount, total_number_format)
            col += 1

        workbook.close()
        output.seek(0)
        return output.read()

    def action_generate_report(self):
        self.ensure_one()

        data = self._get_report_data()

        file_data = self.generate_xlsx_report(data)

        import base64
        file_base64 = base64.b64encode(file_data)

        filename = _('Expense_Report_%s_to_%s.xlsx') % (
            self.date_from.strftime('%Y%m%d'),
            self.date_to.strftime('%Y%m%d')
        )

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/?model=expense.report.wizard&id=%s&field=report_file&download=true&filename=%s' % (
                self.id, filename
            ),
            'target': 'self',
        }

    def button_generate_report(self):
        self.ensure_one()

        if self.date_from > self.date_to:
            raise UserError(_('Date From must be before Date To.'))

        data = self._get_report_data()

        report_data = {
            'wizard_id': self.id,
            'date_from': self.date_from.strftime('%Y-%m-%d'),
            'date_to': self.date_to.strftime('%Y-%m-%d'),
            'company_name': self.company_id.name,
        }

        return {
            'type': 'ir.actions.client',
            'tag': 'aveco_expense_report_download',
            'context': {
                'wizard_id': self.id,
            },
        }
