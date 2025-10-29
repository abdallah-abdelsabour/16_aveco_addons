# -*- coding: utf-8 -*-
# from odoo import http


# class Connected(http.Controller):
#     @http.route('/connected/connected', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/connected/connected/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('connected.listing', {
#             'root': '/connected/connected',
#             'objects': http.request.env['connected.connected'].search([]),
#         })

#     @http.route('/connected/connected/objects/<model("connected.connected"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('connected.object', {
#             'object': obj
#         })
