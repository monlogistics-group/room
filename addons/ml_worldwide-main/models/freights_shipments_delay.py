import json
from odoo import api, fields, models, _
import base64
class FreightShipmentsDelayCategory(models.Model):
    _name = 'freights.shipments.delay.category'
    _description = 'Delay category'

    name = fields.Char(string="Delay category")
    active = fields.Boolean()
    

class FreightShipmentsDelayCategory(models.Model):
    _name = 'freights.shipments.delay'
    _description = 'Delay reason'

    type = fields.Many2one(comodel_name='freights.shipments.delay.category', string="Category")
    name = fields.Char(string="Issue")
    active = fields.Boolean()