# -*- coding: utf-8 -*-
# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2022-11-15

from odoo import models, fields

class TruckingExpenditureData(models.Model):
    _name="mltrucking.expenditure.data"
    _rec_name = 'types'

    types=fields.Char(string='Type')