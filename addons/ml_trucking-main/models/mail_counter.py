# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2022-11-11

from odoo import models, fields

class TruckingMailCounter(models.Model):
    _name = "mltrucking.mail.counter"

    mail_id=fields.Char()
    count=fields.Integer()