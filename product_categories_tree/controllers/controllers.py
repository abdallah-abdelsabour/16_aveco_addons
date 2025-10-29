# -*- coding: utf-8 -*-
# from odoo import http


# class ProductCategoriesTree(http.Controller):
#     @http.route('/product_categories_tree/product_categories_tree', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/product_categories_tree/product_categories_tree/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('product_categories_tree.listing', {
#             'root': '/product_categories_tree/product_categories_tree',
#             'objects': http.request.env['product_categories_tree.product_categories_tree'].search([]),
#         })

#     @http.route('/product_categories_tree/product_categories_tree/objects/<model("product_categories_tree.product_categories_tree"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('product_categories_tree.object', {
#             'object': obj
#         })
