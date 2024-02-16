# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-12-02

from email.policy import default
from odoo import api, fields, models

class FreightsTermsModel(models.Model):
    _name = "freights.terms"
    _description = "Worldwide freights terms model"
    _rec_name = 'terms_name'
    _order = 'sequence asc'

    code = fields.Char(string='Code')
    terms_name = fields.Char(string='Freights terms', )
    
    uses_address = fields.Boolean('Uses Address')
    has_origin_term = fields.Boolean('Origin', default=True)
    has_dest_term = fields.Boolean('Destination', default=False)
    active = fields.Boolean(default=True, string='Active')
    
    sequence = fields.Integer(help="Used to order the note stages")

    _sql_constraints = [('freights_terms_name_unique', 'unique(name)', 'State name already exists')]