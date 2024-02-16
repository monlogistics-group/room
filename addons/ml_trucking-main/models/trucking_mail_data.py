# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2022-11-10

from datetime import date
from email.policy import default
from odoo import api, fields, models

class TruckingMail(models.Model):
    _name = "mltrucking.mail"
    _description = "Ml Trucking mail model"

    greeting=fields.Char(string="Greeting")
    description=fields.Char(string='Description')
    route=fields.Char(string='Route')
    footer=fields.Char(string='footer')
    table_number=fields.Char(string='Table Number')
    table_type=fields.Char(string='Table Type')
    table_id=fields.Char(string='Table ID')
    table_information=fields.Char(string='Table Information')
    price=fields.Char(string='Table price')
    table_estimated_time=fields.Char(string='Estimated Time')
    locale = fields.Many2one(string="Language",comodel_name='res.lang', domain=['|', ('active', '=', False), ('active', '=', True)])
   
   