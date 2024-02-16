# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2023-03-29

from odoo import fields, models

class OriginIncoterms(models.Model):
    _name = 'mltrucking.incoterms'
    _rec_name = 'code'
    _order = 'origin_sequence asc'

    origin_sequence = fields.Integer(string="OS", help="Origin terms sequence")
    code = fields.Char(string='Incoterms code', store=True)
    name = fields.Char(string='Incoterms name', store=True)
    active = fields.Boolean(string='Incoterms active', store=True)
