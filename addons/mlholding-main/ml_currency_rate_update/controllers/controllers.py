# -*- coding: utf-8 -*-
# from odoo import http


# class MltruckingCurrency(http.Controller):
#     @http.route('/mltrucking_currency/mltrucking_currency', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mltrucking_currency/mltrucking_currency/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mltrucking_currency.listing', {
#             'root': '/mltrucking_currency/mltrucking_currency',
#             'objects': http.request.env['mltrucking_currency.mltrucking_currency'].search([]),
#         })

#     @http.route('/mltrucking_currency/mltrucking_currency/objects/<model("mltrucking_currency.mltrucking_currency"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mltrucking_currency.object', {
#             'object': obj
#         })
