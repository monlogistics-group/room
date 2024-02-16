# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-12-02

from odoo import api, fields, models

AVAILABLE_RATE = [
    ('0', 'None'),
    ('1', 'Very Low'),
    ('2', 'Low'),
    ('3', 'Medium'),
    ('4', 'High'),
    ('5', 'Very High'),
]

class FreightsTypeModel(models.Model):
    _name = "freights.agent.review"
    _description = "Worldwide agent reviews"

    review = fields.Char(string="Review", tracking=True,)
    rate = fields.Selection(AVAILABLE_RATE, string='Rate', index=True, default=AVAILABLE_RATE[0][0], tracking=True,)
    
    agent_id = fields.Many2one(comodel_name="res.partner", string="Agent")
    freight_id = fields.Many2one(comodel_name="mlworldwide.freights", string="Freight")