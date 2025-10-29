# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Payslip Customize Fields',
    'version': '1.0.0',
    'author': 'Ahmed Amen',
    'category': 'Accounting/Localizations',
    'license': 'LGPL-3',
    'description': """
    Print Payment QR
""",
    'depends': ['base','hr', 'hr_payroll_account','hr_payroll'],
    'data': [
        'security/access_group.xml',
        'views/employee.xml'
    ],
}
