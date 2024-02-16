# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2022-11-11

from datetime import date
from email.policy import default
from odoo import api, fields, models

class TruckingTransportMail(models.Model):
    _name = "mltrucking.transport.mail"
    _description = "Ml Trucking transport mail model"

    entity=fields.Char(string="Entity")
    container_id=fields.Char(string='Container id')
    count=fields.Char(string='')
    transportations=fields.Char()
    order_num=fields.Char()
    transportation_condition=fields.Char()
    sender=fields.Char()
    employee=fields.Char()
    locale = fields.Many2one(string="Language",comodel_name='res.lang', domain=['|', ('active', '=', False), ('active', '=', True)])
   
   