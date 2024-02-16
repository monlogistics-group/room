from odoo import models, fields
from datetime import datetime

class DemurragesRates(models.Model):
    _name = "ths.rates"
    _description = "ths rates model"
    
    terminal=fields.Many2one('freights.terminal' ,string="Terminal")
    code=fields.Integer(string="Code")
    taras_id = fields.Many2one('freights.taras', string='Taras')
    container =fields.Many2one(comodel_name='freights.container.type' , string=' Container type')
    service_type=fields.Char(string="Service type")
    type_data=fields.Many2one(comodel_name="freights.type", string="Type")
    cost_data=fields.Float(string="Cost")
    start_date =fields.Date(string="Start  ", help="")
    end_date =fields.Date(string="End", help="")
    currency_id = fields.Many2one(comodel_name='res.currency', string="Currency", domain=['|', ('active', '=', False), ('active', '=', True)], default=lambda self: self.env.company.currency_id)
    