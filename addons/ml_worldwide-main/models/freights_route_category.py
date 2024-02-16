import logging
from odoo import api, fields, models, _



class FreightRouteCategory(models.Model):
    _name = 'freights.route.category'
    _description = 'Fcl route'

    name = fields.Char(string='Name')
    active = fields.Boolean(default=True, string='Active')