# -*- coding: utf-8 -*-
# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-11-10

from odoo import models, fields

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    truck_state=fields.Char(string="Truck State")
