# -*- coding: utf-8 -*-
# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2022-12-20

from odoo import models, fields

class ConfirmQuotHeader(models.Model):
    _name = "confirm.quot.header"
    
    greeting=fields.Char(string='Greeting')
    desc=fields.Char(string='Description')
    desc2=fields.Char(string='Desc2')
    desc3=fields.Char(string='Desc3')
    ref=fields.Char(string='Reference number')
    sender=fields.Char(string='Sender')
    trans_condition=fields.Char(string='Transportation condition')
    trans_type=fields.Char(string='Transportation type')
    hscode = fields.Char(string='HSCode')
    ending=fields.Char(string='Ending')
    goods_info = fields.Char(string='Goods Info')
    gross = fields.Char(string='Gross')
    volume = fields.Char(string='Volume')
    package_qty = fields.Char(string='Package qty')
    
    locale = fields.Many2one(string="Language",comodel_name='res.lang', domain=['|', ('active', '=', False), ('active', '=', True)])