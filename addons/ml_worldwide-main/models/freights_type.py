# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-12-02

from odoo import api, fields, models

class FreightsTypeModel(models.Model):
    _name = "freights.type"
    _description = "Worldwide freights type model"
    _order = 'sequence asc'
    _rec_name = 'type_name'

    type_name = fields.Char(string='Freights type', )
    sequence = fields.Integer(help="Used to order the note stages")

    _sql_constraints = [('freights_type_name_unique', 'unique(type_name)', 'Freights type name already exists')]