from odoo import api, fields, models, _



class FreightShippingLine(models.Model):
    _name = 'freights.shipping.line'
    _description = 'Freight Shipping Line'

    name = fields.Char(string='Name')
    active = fields.Boolean(default=True, string='Active')