# -*- coding: utf-8 -*-
# Copyright 2021 Ahmed Amen :  www.linkedin.com/in/ahmed-abdul-khaliq
##############################################################################
from odoo import _, api, fields, models
from odoo.exceptions import UserError,Warning,AccessError
from odoo.tools import float_is_zero, float_compare
from itertools import groupby

import json

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    leave_entitlement = fields.Selection(string="Leave Entitlement",
                                         selection=[('yearly', 'Yearly'), ('2 years', '2 Years')])

    annual_leave_days = fields.Integer(string="Annual Leave Days")
    travel_ticket_value = fields.Float(string="Travel Ticket Value")
    loan_status = fields.Selection(string="Loan status", selection=[('yes', 'Yes'), ('no', 'No')])
    date_last_bouns = fields.Date(string="Date Last End of Service Gratuity", required=False, )
    date_last_bouns_hous = fields.Date(string="Date Last Housing Allowance", required=False, )

    jouin_date = fields.Date(string="Joining Date", required=False, )
    return_date_lst_lev = fields.Date(string="Return Date of Last Leave", required=False, )
    indemnity_date = fields.Date(string="Indemnity Date", required=False, )
    balance = fields.Float(string="Balance", required=False, compute="compute_balance")
    job_num = fields.Char(string="Job Number", required=False, )

    @api.depends('address_home_id')
    def compute_balance(self):
        for rec in self:
            credit = 0.0
            debit = 0.0
            if rec.address_home_id:
                moves = self.env['account.move.line'].sudo().search(
                    [('move_id.state', '=', 'posted'), ('partner_id', '=', rec.address_home_id.id)])
                credit = sum(moves.mapped('credit'))
                debit = sum(moves.mapped('debit'))
            rec.balance = debit - credit


class hr_salary_rule(models.Model):
    _inherit = 'hr.salary.rule'

    due_salary = fields.Boolean(string="Due Salary", )





