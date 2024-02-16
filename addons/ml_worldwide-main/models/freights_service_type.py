# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-12-02

from datetime import datetime
from email.policy import default
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class FreightsServicesTypeModel(models.Model):
    _name = "freights.service.type"
    _description = "Worldwide freights service model"
    _order = 'sequence asc'
    
    name = fields.Char(string="name")
    product_id = fields.Many2one('product.product', string='Product', copy=False,)
    sequence = fields.Integer(help="Used to order the service type")

    _sql_constraints = [('freights_service_type_name_unique', 'unique(name)', 'Service type already exists')]
