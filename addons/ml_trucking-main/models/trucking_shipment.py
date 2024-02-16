# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2022-10-26

from email.policy import default
from odoo import api, fields, models

class TruckingShipment(models.Model):
    _name = "mltrucking.shipment"
    _description = "Ml Truckin shipment model"
    _rec_name='vehicle'
   
    net_distance=fields.Integer(string='Net distance')
    total_distance=fields.Integer(string='Total distance')
    vehicle=fields.Many2one('fleet.vehicle',string='Vehicle')
    vehicle_rel_id=fields.Integer(related="vehicle.id")
    vehicle_rel=fields.Char(related="vehicle.display_name", string="Vehicle")
    state = fields.Selection([
        ('ready', 'Ready'),
        ('not_ready', 'Not ready')
        ], string='Service state', readonly=True, tracking=True)
    
    color = fields.Integer('Color', compute='_get_color')
    
    def _get_color(self):
        """Compute Color value according to the conditions"""
        for rec in self:
            if rec.state == "ready":
                rec.color = 3
            elif rec.state == 'not_ready':
                rec.color = 4
            else:
                rec.color=2

    @api.onchange('vehicle')
    def onchange_vehicle(self):
        # a=self.env['mltrucking.package'].search([('shipment', '=',self.vehicle_rel)])
        # print(a.id)
        print(self.vehicle_rel,'===========================')