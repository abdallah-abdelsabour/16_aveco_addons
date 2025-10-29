# -*- coding: utf-8 -*-
{
    'name': "Branch ",

    'summary': """
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "",
    'website': "https://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'account', 'sale'],

    # always loaded
    'data': [
        'security/res_branch.xml',
        'security/ir.model.access.csv',
        'views/res_branch.xml',
        'views/inherited_views.xml',
    ],

    'demo': [
    ],
}
