# -*- coding: utf-8 -*-
{
    'name': "Custody Management",

    'summary': """
     Custody Management
    """,
    'author': "Yahia Saleh",
    'website': "yahiasaleh911@gmail.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '16.0',

    # any module necessary for this one to work correctly
    'depends': ['account', 'project'],
    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/custody_views.xml',
        'views/res_config_settings.xml',
        'views/menus.xml'
    ]
}
