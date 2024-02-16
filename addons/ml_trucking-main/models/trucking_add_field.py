# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2022-11-01

import types
from odoo import api, fields, models

class TruckingAddField(models.Model):
    _inherit="res.partner" 
    
    truck_types = fields.Many2many(comodel_name= "mltrucking.type", string="Truck types")
    other_lang = fields.Many2many(comodel_name='res.lang', string="Other language", domain=['|', ('active', '=', False), ('active', '=', True)]) 
    is_employee=fields.Boolean(string='IsEmployee')
    
    