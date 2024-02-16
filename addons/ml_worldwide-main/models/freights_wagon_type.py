from odoo import api, fields, models, _



class FreightWagonType(models.Model):
    _name = 'freights.wagon.type'
    _description = 'Freight Wagon Type'

    name = fields.Char(string='Name')
    active = fields.Boolean(default=True, string='Active')