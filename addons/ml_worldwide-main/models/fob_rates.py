from odoo import models, fields
from datetime import datetime

class FobRates(models.Model):
    _name = "fob.rates"
    _description = "fob rates model"
    
    selection=fields.Char('Selection')
    empty=fields.Char(string="Empty return")
    startdate = fields.Date(string='Start date')
    enddate = fields.Date(string='End date')
    ett=fields.Float(string="ETT")
    cost_data=fields.Float(string="Cost")
    
    agent_data = fields.Many2one(comodel_name="res.partner", string="Agent", help="Захиалга өгсөн менежерийн нэр")
    from_data=fields.Many2one(comodel_name='freights.points' ,string="From")
    to_data=fields.Many2one(comodel_name='freights.points' ,string="To")
    terminal=fields.Many2one('freights.terminal' ,string="Terminal")
    taras_data=fields.Many2one('freights.taras', string='Taras')
    currency_id = fields.Many2one(comodel_name='res.currency', string="Currency", domain=['|', ('active', '=', False), ('active', '=', True)], default=lambda self: self.env.company.currency_id)
    