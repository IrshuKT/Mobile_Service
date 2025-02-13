# -*- coding: utf-8 -*-
# from odoo import http


# class Mobileservice(http.Controller):
#     @http.route('/mobileservice/mobileservice', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mobileservice/mobileservice/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mobileservice.listing', {
#             'root': '/mobileservice/mobileservice',
#             'objects': http.request.env['mobileservice.mobileservice'].search([]),
#         })

#     @http.route('/mobileservice/mobileservice/objects/<model("mobileservice.mobileservice"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mobileservice.object', {
#             'object': obj
#         })
