# -*- coding: utf-8 -*-
{
    'name': "company_branch",
    'summary': """ """,
    'description': """ """,
    'author': "me",
    'website': "https://www.yourcompany.com",
    'category': 'Customization',
    'version': '0.1',
    'depends': ['base', 'sale', 'account', 'contacts'],

    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/views.xml',
        'views/inhert_sale_account.xml'

    ],

}
