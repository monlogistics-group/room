# -*- coding: utf-8 -*-
# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-10-25

from odoo import fields, models

class TruckingCore(models.Model):
    _name = "mltrucking.core"
    _description="mltrucking create core"
    
    truck_quotation=fields.Many2one(comodel_name="mltrucking.base", string='Quotation', readonly=True, store=True)  #related='core_id.truck_quotation',
    truck_order=fields.Many2one(comodel_name="mltrucking.base", string='Order', readonly=True, store=True)
    truck_state = fields.Char(required=True, translate=True, readonly=True, store=True)