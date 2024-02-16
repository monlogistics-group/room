# -*- coding: utf-8 -*-
# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2023-01-03

from odoo import models, fields

class FreightStations(models.Model):
    _name = "freight.stations"
    _order = "create_date"

    code = fields.Char(string='Code')
    director = fields.Char(string='Director')
    contact = fields.Char(string='mlw Contact')
    name = fields.Char(string='Name')
    prefix = fields.Boolean(string='stPrefix')
    transporter = fields.Char(string='Transporter')
    ubtz_code = fields.Char(string='ubtz Code')
    ubtz_country_code = fields.Char(string='ubtz CountryCode')


