# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-10-24

from odoo import api, fields, models

class TruckingTypeModel(models.Model):
    _name = "mltrucking.type"
    _description = "ML Trucking type model"
    _order = 'sequence asc'
    _rec_name = 'type_name'

    type_name = fields.Char(string='Trucking type', )
    sequence = fields.Integer(help="Used to order the note stages")

    _sql_constraints = [('trucking_type_name_unique', 'unique(type_name)', 'Track type name already exists')]

# class ResPartner(models.Model):
#     _inherit = 'res.partner'

#     type_name = fields.Many2many(comodel_name="mltrucking.type", string="Type", help="Trucking type",)