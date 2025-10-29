# -*- coding: utf-8 -*-
{
    'name': "Product Categories Tree",

    'summary': """
        This application helps in categorizing product categories into main and subcategories and generates a code for each product category.""",

    'description': """
        This application helps in categorizing product categories into main and subcategories and generates a code for each product category.
        
        The code is generated based on the main category and subcategory.
        
        It also assists the user in easily identifying the product by the category code.
    """,

    'author': "ISSOLUTION TECH",
    'website': "http://issolutiontech.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Construction Solutions',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
