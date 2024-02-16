from odoo import api, fields, models, _



class FreighTruckType(models.Model):
    _name = 'freights.truck.type'
    _description = 'Freight Truck Type'

    name = fields.Char(string='Name')
    active = fields.Boolean(default=True, string='Active')