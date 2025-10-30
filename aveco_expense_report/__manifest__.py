{
    'name': "AVECO Expense Report",
    'version': '16.0.1.0.0',
    'category': 'Accounting/Reporting',
    'summary': """Generate Excel expense reports by analytic accounts with advanced filters""",
    'description': """
AVECO Expense Report Module

This module provides advanced expense reporting capabilities:
- Filter by date range
- Filter by posted/all entries
- Filter by analytic accounts (creates dynamic columns)
- Filter by account codes and ranges
- Filter by account groups
- Export to Excel with Arabic RTL layout
- Supports multi-company operations
    """,
    'author': 'Abdallah salem',
    'website': "https://github.com/abdallah-abdelsabour",
    'depends': [
        'base',
        'account',
        'analytic',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/wizard_views.xml',
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'aveco_expense_report/static/src/js/report_action.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
