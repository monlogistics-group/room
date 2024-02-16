from odoo import api, fields, models, _

class FreightShipmentType(models.Model):
    _name = 'freights.shipment.type'
    _description = 'Shipment Type'

    # Container, Wagom, Bill, Vehicle
    name = fields.Char(string='Name')
    active = fields.Boolean(default=True, string='Active')