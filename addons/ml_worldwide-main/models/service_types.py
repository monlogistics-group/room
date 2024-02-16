# -*- coding: utf-8 -*-
# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>

from odoo import models, fields

class ServiceTypes(models.Model):
    _name = "service.types"
    _rec_name = "purpose"

    type = fields.Many2one('freights.service.type')
    purpose = fields.Char()