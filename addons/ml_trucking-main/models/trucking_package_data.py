# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2022-11-21

from datetime import date
from email.policy import default
from odoo import api, fields, models

class TruckingPackage(models.Model):
    _name = "mltrucking.package.data"
    _description = "Ml Truckin package data model"
    _rec_name='data_types'
    
    data_types=fields.Char()