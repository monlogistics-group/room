from odoo import models, fields

class DeliveryVehicle(models.Model):
    _name= "delivery.vehicle"
    
    name = fields.Char(string="name")
    active = fields.Boolean(string="Active")
    sequence = fields.Integer(string="sequence")
    
    
    
class DeliveryZone(models.Model):
    _name= "delivery.zone"
    
    name = fields.Char(string="name")
    active = fields.Boolean(string="Active")
    sequence = fields.Integer(string="sequence")