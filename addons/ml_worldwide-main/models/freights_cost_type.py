# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-12-02

from datetime import datetime
from email.policy import default
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class FreightsCostTypeModel(models.Model):
    _name = "freights.cost.type"
    _description = "Worldwide freights cost model"
    _order = 'sequence asc'
    
    name = fields.Char(string="name")
    sequence = fields.Integer(help="Used to order the cost type")
    _sql_constraints = [('freights_cost_type_name_unique', 'unique(name)', 'cost type already exists')]
