# -*- coding: utf-8 -*-
# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2022-12-19

from odoo import models, fields

class ConfirmAgentQuotation(models.Model):
    _name = "confirm.agent.quotation"

    greeting=fields.Char(string='Greeting')
    desc=fields.Char(string="Description")
    desc2=fields.Char(string='Desc2')
    desc3=fields.Char(string='Desc3')
    ref=fields.Char(string='Reference Number')
    shipper=fields.Char(string='Shipper')
    consignee=fields.Char(string='Consignee')
    hs_code=fields.Char(string='HS Code')
    cargo_detail=fields.Char(string='Cargo Detail')
    freight_type=fields.Char(string='Freight type')
    ending=fields.Char(string='Ending')
    
    locale = fields.Many2one(string="Language",comodel_name='res.lang', domain=['|', ('active', '=', False), ('active', '=', True)])