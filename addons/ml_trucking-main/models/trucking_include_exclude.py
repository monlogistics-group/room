# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2023-10-11

from odoo import fields, models

class OriginIncoterms(models.Model):
    _name = 'mltrucking.include.exclude'
    # _rec_name = 'code'
    # _order = 'origin_sequence asc'

    include_service = fields.Char(string='Include service', store=True)
    not_include_service = fields.Char(string='Not Include service', store=True)
