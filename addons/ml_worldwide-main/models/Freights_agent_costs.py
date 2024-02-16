
import datetime
from email.policy import default
from odoo import api, fields, models
import requests
import json

class FreightsAgentCostModel(models.Model):
    _name = 'freights.agent.cost'
    _description = 'Agent cost'
    _rec_name = 'agent_id'

    service_cost = fields.Float(string='Cost', help="", ) 
    valid_until_date = fields.Date(string="Valid Until date", help="")
    ett = fields.Integer(string="ETT",help="")
    remark = fields.Char('Remark')
    
    transport_type = fields.Many2one(comodel_name="mlworldwide.transport.type", string='Transport type', )
    agent_id = fields.Many2one(comodel_name="res.partner", string="Agent", help="Захиалга өгсөн менежерийн нэр",) 
    currency_id = fields.Many2one(comodel_name='res.currency', string="Currency", domain=[ ('active', '=', True)], default=lambda self: self.env.company.currency_id)
    


