# -*- coding: utf-8 -*-
# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-12-02

from odoo import models, fields

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    freight_state=fields.Char(string="Freigth State")
