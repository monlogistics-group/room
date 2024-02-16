from odoo import api, fields, models, _

class WorldwideTransportType(models.Model):
    _name = 'mlworldwide.transport.type'
    _description = 'Freight Transport Type'

    name = fields.Char(string='Name')
    active = fields.Boolean(default=True, string='Active')