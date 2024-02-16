# -*- coding: utf-8 -*-
# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-12-05

from odoo import models, fields

class HREmployee(models.Model):
    _inherit = "hr.employee"

    # user_groups=fields.Many2many(comodel_name='mlworldwide.user.groups', string="User groups")
    user_freight_types=fields.Many2many(comodel_name='freights.type', string="User freight types")

    blank_stamp=fields.Image( string="Stamp")
    
    blank_signature=fields.Binary( string="Signature")