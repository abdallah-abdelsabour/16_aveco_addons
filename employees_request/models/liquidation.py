# -*- coding: utf-8 -*-
# Copyright 2021 Ahmed Amen :  www.linkedin.com/in/ahmed-abdul-khaliq
##############################################################################
from odoo import _, api, fields, models
from odoo.exceptions import UserError,Warning,AccessError,ValidationError
from odoo.tools import float_is_zero, float_compare
from itertools import groupby

import json
# import datetime
# import dateutil.relativedelta
from datetime import date, timedelta

class liquidation_dues(models.Model):
    _name = "liquidation.dues"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    rec_name = 'name'

    name = fields.Char(string="Liquidation",  readonly=True)
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=True, tracking=True,)
    contract_id = fields.Many2one(comodel_name="hr.contract", string="Contract", related="employee_id.contract_id",required=True ,tracking=True,)
    contract_start_date = fields.Date(string="Contract Start Date", related="contract_id.first_contract_date",tracking=True,)
    wage = fields.Float(string="Wage",tracking=True,compute="cont_end_date")
    gross = fields.Float(string="Gross",tracking=True,compute="cont_end_date")
    contract_end_date = fields.Date(string="Contract End Date",tracking=True,compute="cont_end_date")
    request_date = fields.Date(string="Request Date", required=True,tracking=True, )
    jouin_date = fields.Date(string="Joining Date",related="employee_id.jouin_date",  required=False,tracking=True, )
    return_date_lst_lev = fields.Date(string="Return Date of Last Leave",related="employee_id.return_date_lst_lev", tracking=True, )
    indemnity_date = fields.Date(string="Indemnity Date", required=False,related="employee_id.indemnity_date",tracking=True,  )
    residency_num = fields.Char(string="Residency Number", required=False,related="employee_id.residency_num", tracking=True, )
    passport_num = fields.Char(string="Passport Number", required=False,related="employee_id.passport_num", tracking=True, )
    job_num = fields.Char(string="Job Number", required=False,related="employee_id.job_num", tracking=True, )

    balance = fields.Float(string="Balance", required=False, compute="cal_balance_flag",)
    balance_flag = fields.Char(string="Balance Flag", required=False, compute="cal_balance_flag")
    priv_salary = fields.Float(string="Previous month's salary",  required=False, compute='check_salary')
    current_salary = fields.Float(string="Current Month's Salary",  required=False, compute='check_salary')
    extra_hours = fields.Float(string="Extra Hours",  required=False,tracking=True,)
    other_allowance = fields.Float(string="Other allowances",  required=False,tracking=True,)
    other_allowance_fixed = fields.Float(string="Other allowances Fixed",compute='total_allowances_fixed', required=False, )
    note_allowance = fields.Char(string="Note allowances",  required=False,tracking=True,)
    end_ser5y = fields.Float(string="End of service allowance for 5 years",  required=False,tracking=True,)
    end_ser_after5y = fields.Float(string="End of service allowance After 5 years",  required=False,tracking=True,)
    leave_allowance = fields.Float(string="Leave Allowance",  required=False,tracking=True,)
    air_alns = fields.Float(string="Air Ticket Allowance",  required=False,tracking=True,)
    total_alns = fields.Float(string="Total Allowances",  required=False, compute='total_allowances')

    all_dtct = fields.Float(string="Total Deductions",  required=False,tracking=True,)
    custody = fields.Float(string="custody",  required=False,tracking=True,)
    other_dtct = fields.Float(string="Other Deductions", required=False,tracking=True,)
    note_dtact = fields.Char(string="Note Deductions", required=False,tracking=True,)
    total_dtct = fields.Float(string="Total Deductions", required=False, compute='total_deductions')

    bonus = fields.Float(string="Bonus", required=False,tracking=True,)
    other_info = fields.Float(string="Other Info", required=False,tracking=True,)
    other_info_note = fields.Char(string="Other Info Note", required=False,tracking=True,)
    total_net = fields.Float(string="Total Net", required=False, compute='compute_total_net')

    state = fields.Selection(string="State", selection=[('draft', 'Draft'), ('confirm', 'Confirmed'),('paid', 'Paid'), ], tracking=True,required=False,default='draft' )
    days_number = fields.Char(string="Days Number", required=False, compute="compute_days_number")
    days_num_lst_lev = fields.Char(string="Days Number From Last Leave", required=False,compute="compute_days_num_lst_lev" )


    @api.depends('contract_id')
    def total_allowances_fixed(self):
        for rec in self:
            amount_fix = 0.0
            if rec.contract_id and rec.contract_id.structure_type_id and rec.contract_id.structure_type_id.default_struct_id:
                rule_ids = rec.contract_id.structure_type_id.default_struct_id.rule_ids
                for rule in rule_ids:
                    if rule.category_id.code == 'ALW' and rule.amount_fix:
                        amount_fix += rule.amount_fix
            rec.other_allowance_fixed = amount_fix



    @api.depends('employee_id', 'request_date')
    def compute_days_num_lst_lev(self):
        days_num = ""

        if self.employee_id and self.employee_id.return_date_lst_lev and self.request_date:
            start_date = self.employee_id.return_date_lst_lev
            d1 = fields.Datetime.from_string(self.request_date)
            d2 = fields.Datetime.from_string(start_date)
            delta = d1 - d2
            days = delta.days + 1
            days_num = str(days) + ' يوم '
        self.days_num_lst_lev = days_num

    @api.depends('employee_id','request_date')
    def compute_days_number(self):
        days_num = ""

        if self.employee_id and self.employee_id.contract_ids and self.request_date:
            first_contract = self.employee_id.contract_ids[0]
            start_date = first_contract.date_start
            print("start_date ==> ",start_date)
            d1 = fields.Datetime.from_string(self.request_date)
            d2 = fields.Datetime.from_string(start_date)
            delta = d1 - d2
            days = delta.days + 1
            days_num = str(days) + ' يوم '
        self.days_number = days_num

    def unlink(self):
        if any(rec.state != 'draft' for rec in self):
            raise ValidationError(_('You cannot delete records if they are in non-draft state'))
        return super(liquidation_dues, self).unlink()


    @api.depends('balance','employee_id')
    def cal_balance_flag(self):
        for rec in self:
            flag = ""
            balance = rec.employee_id.balance
            print("*** balance ==> ",balance)
            if balance > 0:
                flag = 'دائن'
            if balance < 0:
                flag = 'مدين'
            rec.balance_flag = flag
            rec.balance = abs(balance)


    @api.depends('contract_id')
    def cont_end_date(self):
        self.contract_end_date = self.contract_id.date_end or self.request_date
        payslip = self.env['hr.payslip.line'].sudo().search(
            [('employee_id', '=', self.employee_id.id), ('slip_id.state', '=', 'done'),('code', '=', 'GROSS')],limit=1, order='id DESC')

        self.wage = self.contract_id.wage or 0.0
        self.gross = payslip.total or 0.0

    @api.depends('bonus', 'other_info', 'total_dtct', 'total_alns')
    def compute_total_net(self):
        self.total_net = self.total_alns - self.total_dtct + self.bonus + self.other_info

    @api.depends('all_dtct', 'custody', 'other_dtct', 'other_allowance')
    def total_deductions(self):
        self.total_dtct = self.all_dtct +self.custody+self.other_dtct



    @api.depends('priv_salary','current_salary','extra_hours','other_allowance','end_ser5y','end_ser_after5y','leave_allowance','air_alns',)
    def total_allowances(self):
        self.total_alns =self.priv_salary+self.current_salary+self.extra_hours+ self.other_allowance +self.end_ser5y+self.end_ser_after5y+self.leave_allowance+self.air_alns


    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('dues.order') or _('New')
        return super(liquidation_dues, self).create(values)

    @api.depends('request_date','employee_id')
    def check_salary(self):
        """ Get Deu lines only"""
        amt = 0.0
        crnt_amt = 0.0
        if self.request_date and self.employee_id:
            prev = self.request_date.replace(day=1) - timedelta(days=1)
            mnth_prev = prev.replace(day=15)
            print("mnth_prev ==> ",mnth_prev)
            payslip_obj = self.env['hr.payslip'].sudo().search([('employee_id', '=', self.employee_id.id),
                                                         ('state', '=', 'done'), ('date_from', '<=', mnth_prev),
                                                         ('date_to', '>=', mnth_prev)],limit=1)

            print("payslip_obj ==> ", payslip_obj)
            print("payslip_obj.line_ids: ==> ", payslip_obj.line_ids)

            if payslip_obj:
                for line in payslip_obj.line_ids:
                    if line.salary_rule_id.due_salary:
                        amt += line.total
            currant = self.request_date.replace(day=15)
            curnt_payslip = self.env['hr.payslip'].sudo().search([('employee_id', '=', self.employee_id.id),
                                                        ('state', '=', 'done'), ('date_from', '<=', currant),
                                                        ('date_to', '>=', currant)], limit=1)

            print("curnt_payslip ==> ", curnt_payslip)

            if curnt_payslip:
                for crnt in curnt_payslip.line_ids:
                    if crnt.salary_rule_id.due_salary:
                        crnt_amt += crnt.total
        self.current_salary = crnt_amt
        self.priv_salary = amt



    def action_confirm(self):
        self.state = 'confirm'