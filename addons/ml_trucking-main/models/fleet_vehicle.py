# -*- coding: utf-8 -*-
# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-11-21

from odoo import models, fields

class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    truck_gps_id = fields.Char(string='GPS id',)
    truck_location_id = fields.Many2many(comodel_name='mltrucking.location', string="Location", compute ="read_location")
    
    def read_location(self):
        self.sudo().truck_location_id = []
        self.sudo().truck_location_id = self.env["mltrucking.location"].search([("fleet_id","=",self.id)])