from odoo import models, fields
from datetime import datetime

class DeliveryRates(models.Model):
    _name = "delivery.rates"
    _description = "delivery rates model"
    
    cost_data=fields.Float(string="Cost")
    start_date =fields.Date(string="Start ", help="")
    end_date =fields.Date(string="End ", help="")
    
    fleet=fields.Many2one('delivery.vehicle' , string="Vehicle")  # Vehicle
    currency_id = fields.Many2one(comodel_name='res.currency', string="Currency", domain=['|', ('active', '=', False), ('active', '=', True)], default=lambda self: self.env.company.currency_id)
    terminal=fields.Many2one('freights.terminal' ,string="Terminal")
    delivery_zone=fields.Many2one('delivery.zone',string="Delivery zone")
    agent_id = fields.Many2one(comodel_name="res.partner", string="Agent", help="Delivery LLC нэр", domain="[('agent','=', True), ('is_company', '=', True)]")
