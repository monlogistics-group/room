# -*- coding: utf-8 -*-
# from odoo import http


# class WorldwideGmail(http.Controller):
#     @http.route('/worldwide_gmail/worldwide_gmail', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/worldwide_gmail/worldwide_gmail/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('worldwide_gmail.listing', {
#             'root': '/worldwide_gmail/worldwide_gmail',
#             'objects': http.request.env['worldwide_gmail.worldwide_gmail'].search([]),
#         })

#     @http.route('/worldwide_gmail/worldwide_gmail/objects/<model("worldwide_gmail.worldwide_gmail"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('worldwide_gmail.object', {
#             'object': obj
#         })
