{
    'name': 'Custom Branch Module',
    'version': '1.0',
    'category': 'Custom',
    'author': 'Your Name',
    'depends': ['base', 'sale', 'account'],
    'data': [
        'security/ir_rule.xml',
        'security/ir.model.access.csv',

        'views/branch_view.xml',

    ],
    'installable': True,
    'auto_install': False,
}
