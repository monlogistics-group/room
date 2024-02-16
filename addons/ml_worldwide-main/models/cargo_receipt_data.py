# -*- coding: utf-8 -*-
# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2023-04-13

from odoo import models, fields

class CargoReceiptData(models.Model):
    _name = "cargo.receipt.data"

    title = fields.Char(string='Title')
    ref = fields.Char(string='Ref')
    type = fields.Char(string='Type')
    date = fields.Char(string='Date')
    address = fields.Char(string='address')
    goods_name = fields.Char(string='Name')
    quantity = fields.Char(string='Quantity')
    terminal = fields.Char()
    shipper = fields.Char(string='Shipper')
    consignee_company = fields.Char(string='Consignee')
    condition = fields.Char()
    operation = fields.Char()
    container_num = fields.Char()
    arrived_date = fields.Char()
    received_date = fields.Char()
    note = fields.Char()
    freight_forwarder = fields.Char()
    name = fields.Char()
    cargo = fields.Char()
    forwarder_signature = fields.Char()
    consignee = fields.Char()
    consignee_name = fields.Char()
    consignee_signature = fields.Char()
    notice = fields.Char()
    data = fields.Char()
    locale = fields.Many2one(string="Language",comodel_name='res.lang', domain=['|', ('active', '=', False), ('active', '=', True)])