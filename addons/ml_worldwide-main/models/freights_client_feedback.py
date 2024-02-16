# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-12-02

from odoo import api, fields, models
from datetime import date

AVAILABLE_RATE = [
    ('0', 'None'),
    ('1', 'Very Low'),
    ('2', 'Low'),
    ('3', 'Medium'),
    ('4', 'High'),
    ('5', 'Very High'),
]

class FreightsTypeModel(models.Model):
    _name = "freights.client.feedback"
    _description = "Client feedbacks"

    review = fields.Text(string="Review")
    expire_date = fields.Date()
    rate = fields.Selection(
        AVAILABLE_RATE, string='Rate', index=True,
        default=AVAILABLE_RATE[0][0])
        
    agent_id = fields.Many2one(comodel_name="res.partner", string="Client")
    freight_id = fields.Many2one(comodel_name="mlworldwide.freights", string="Freight")