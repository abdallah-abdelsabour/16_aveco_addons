# -*- coding: utf-8 -*-
# from odoo import http


# class TenderCosting(http.Controller):
#     @http.route('/tender_costing/tender_costing', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tender_costing/tender_costing/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('tender_costing.listing', {
#             'root': '/tender_costing/tender_costing',
#             'objects': http.request.env['tender_costing.tender_costing'].search([]),
#         })

#     @http.route('/tender_costing/tender_costing/objects/<model("tender_costing.tender_costing"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tender_costing.object', {
#             'object': obj
#         })
