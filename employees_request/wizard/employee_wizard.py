# # -*- coding: utf-8 -*-
#
from odoo import models, fields, api


class EmployeeWizard(models.TransientModel):
    _name = "employee.wizard"

    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)
    req_salary_acc_debit_id = fields.Many2one(comodel_name="account.account", string="Salary Debit Account")
    req_salary_acc_credit_id = fields.Many2one(comodel_name="account.account", string="Salary Credit Account")
    req_salary_journal_id = fields.Many2one(comodel_name="account.journal", string="Salary Jornal")

    req_leave_acc_debit_id = fields.Many2one(comodel_name="account.account", string="Leave Debit Account")
    req_leave_acc_credit_id = fields.Many2one(comodel_name="account.account", string="Leave Credit Account")
    req_leave_journal_id = fields.Many2one(comodel_name="account.journal", string="Leave Journal")

    req_overtime_acc_debit_id = fields.Many2one(comodel_name="account.account", string="Overtime Debit Account")
    req_overtime_acc_credit_id = fields.Many2one(comodel_name="account.account", string="Overtime Credit Account")
    req_overtime_journal_id = fields.Many2one(comodel_name="account.journal", string="Overtime Journal")

    req_hous_acc_debit_id = fields.Many2one(comodel_name="account.account", string="Housing Debit Account")
    req_hous_acc_credit_id = fields.Many2one(comodel_name="account.account", string="Housing Credit Account")
    req_hous_journal_id = fields.Many2one(comodel_name="account.journal", string="Housing Journal")

    req_endserv_acc_debit_id = fields.Many2one(comodel_name="account.account", string="End of Service Debit Account")
    req_endserv_acc_credit_id = fields.Many2one(comodel_name="account.account", string="End of Service Account")
    req_endserv_journal_id = fields.Many2one(comodel_name="account.journal", string="End of Service Journal")

    def action_save(self):
        if self.req_salary_acc_debit_id:
            self.company_id.req_salary_acc_debit_id = self.req_salary_acc_debit_id.id
        if self.req_salary_acc_credit_id:
            self.company_id.req_salary_acc_credit_id = self.req_salary_acc_credit_id.id
        if self.req_salary_journal_id:
            self.company_id.req_salary_journal_id = self.req_salary_journal_id.id
        # ============================================================================
        if self.req_leave_acc_debit_id:
            self.company_id.req_leave_acc_debit_id = self.req_leave_acc_debit_id.id
        if self.req_leave_acc_credit_id:
            self.company_id.req_leave_acc_credit_id = self.req_leave_acc_credit_id.id
        if self.req_leave_journal_id:
            self.company_id.req_leave_journal_id = self.req_leave_journal_id.id
        # ===========================================================================
        if self.req_overtime_acc_debit_id:
            self.company_id.req_overtime_acc_debit_id = self.req_overtime_acc_debit_id.id
        if self.req_overtime_acc_credit_id:
            self.company_id.req_overtime_acc_credit_id = self.req_overtime_acc_credit_id.id
        if self.req_overtime_journal_id:
            self.company_id.req_overtime_journal_id = self.req_overtime_journal_id.id
        # ===========================================================================
        if self.req_hous_acc_debit_id:
            self.company_id.req_hous_acc_debit_id = self.req_hous_acc_debit_id.id
        if self.req_hous_acc_credit_id:
            self.company_id.req_hous_acc_credit_id = self.req_hous_acc_credit_id.id
        if self.req_hous_journal_id:
            self.company_id.req_hous_journal_id = self.req_hous_journal_id.id
            # ===========================================================================
        if self.req_endserv_acc_debit_id:
            self.company_id.req_salary_acc_debit_id = self.req_salary_acc_debit_id.id
        if self.req_endserv_acc_credit_id:
            self.company_id.req_endserv_acc_credit_id = self.req_endserv_acc_credit_id.id
        if self.req_endserv_journal_id:
            self.company_id.req_endserv_journal_id = self.req_endserv_journal_id.id

    @api.onchange('company_id')
    def company_save(self):
        if self.company_id.req_salary_acc_debit_id:
            self.req_salary_acc_debit_id = self.company_id.req_salary_acc_debit_id.id
        if self.company_id.req_salary_acc_credit_id:
            self.req_salary_acc_credit_id = self.company_id.req_salary_acc_credit_id.id
        if self.company_id.req_salary_journal_id:
            self.req_salary_journal_id = self.company_id.req_salary_journal_id.id
            # ===========================================================================
        if self.company_id.req_leave_acc_debit_id:
            self.req_leave_acc_debit_id = self.company_id.req_leave_acc_debit_id.id
        if self.company_id.req_leave_acc_credit_id:
            self.req_leave_acc_credit_id = self.company_id.req_leave_acc_credit_id.id
        if self.company_id.req_leave_journal_id:
            self.req_leave_journal_id = self.company_id.req_leave_journal_id.id
            # ===========================================================================
        if self.company_id.req_overtime_acc_debit_id:
            self.req_overtime_acc_debit_id = self.company_id.req_overtime_acc_debit_id.id
        if self.company_id.req_overtime_acc_credit_id:
            self.req_overtime_acc_credit_id = self.company_id.req_overtime_acc_credit_id.id
        if self.company_id.req_overtime_journal_id:
            self.req_overtime_journal_id = self.company_id.req_overtime_journal_id.id
            # ===========================================================================
        if self.company_id.req_hous_acc_debit_id:
            self.req_hous_acc_debit_id = self.company_id.req_hous_acc_debit_id.id
        if self.company_id.req_hous_acc_credit_id:
            self.req_hous_acc_credit_id = self.company_id.req_hous_acc_credit_id.id
        if self.company_id.req_hous_journal_id:
            self.req_hous_journal_id = self.company_id.req_hous_journal_id.id
            # ===========================================================================
        if self.company_id.req_endserv_acc_debit_id:
            self.req_endserv_acc_debit_id = self.company_id.req_endserv_acc_debit_id.id
        if self.company_id.req_endserv_acc_credit_id:
            self.req_endserv_acc_credit_id = self.company_id.req_endserv_acc_credit_id.id
        if self.company_id.req_endserv_journal_id:
            self.req_endserv_journal_id = self.company_id.req_endserv_journal_id.id

