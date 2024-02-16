# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-12-02

from odoo import api, fields, models

class FreightsTypeModel(models.Model):
    _name = "freights.ability"
    _description = "Worldwide freights abilities"
    _rec_name = 'type_name'

    type_name = fields.Char(string='Ability', )
    _sql_constraints = [('freights_ability_name_unique', 'unique(type_name)', 'Freights ability already exists')]