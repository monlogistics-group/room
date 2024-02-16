# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2023-5-10

from email.policy import default
from odoo import api, fields, models

class QuotationAgentsMail(models.Model):
    _name = 'quotation.agents.mail'
    
    agent = fields.Many2one('res.partner')
    contacts = fields.Many2many('res.partner', string='Shipment Order Mails')
    service_id = fields.Many2one('freights.service')


  