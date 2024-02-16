# -*- coding: utf-8 -*-
# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2023-03-27

from odoo import models, fields

class ArrivalNotice(models.Model):
    _name = "arrival.notice"

    greetings = fields.Char(string='Greetings')
    title = fields.Char(string='Title')
    ref = fields.Char(string='Ref')
    type = fields.Char(string='Freight Type')
    terminal = fields.Char(string='Terminal')
    contact = fields.Char(string='Contact')
    contribute = fields.Char(string='Contribute')
    ata = fields.Char(string='Ata')
    transit_time = fields.Char(string='Transit Time')
    subTitle = fields.Char(string='Sub Title')
    container_ref = fields.Char(string='Container Ref')
    cargo_name = fields.Char(string='Cargo Name')
    shipper = fields.Char(string='Shipper')
    detail = fields.Char(string='Detail')
    
    lang = fields.Many2one(string="Language",comodel_name='res.lang', domain=['|', ('active', '=', False), ('active', '=', True)])