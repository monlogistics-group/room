from odoo import api, fields, models, _

class InsuranceCost(models.Model):
    _name = "insurance.cost"
    _description = ''

    freight_type = fields.Many2one(comodel_name="freights.type", string="Freight type")
    cost= fields.Float(string="Cost")
    cost_currency = fields.Many2one(comodel_name='res.currency', string="Currency", domain=[('active', '=', True)], default=lambda self: self.env.company.currency_id)