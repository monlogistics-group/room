# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Ariuka. 2022-10-27

from odoo import api, fields, models

class TruckingPortModel(models.Model):
    _name = "mltrucking.port"
    _description = "Ml Truckins port model"
    _rec_name = 'name'


    code = fields.Char(string = "Code")
    name = fields.Char(string = "Name")
    country = fields.Many2one(string="Country",comodel_name="res.country")
    fed_state = fields.Many2many(comodel_name="res.country.state")
    is_active = fields.Boolean(string="Active", default=False)
    is_air = fields.Boolean(string="Air", default=False)
    is_ocean = fields.Boolean(string="Ocean", default=False)
    is_land = fields.Boolean(string="Land", default=False)
    