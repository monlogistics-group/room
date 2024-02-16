from odoo import models, fields
from datetime import datetime

class DemurragesRates(models.Model):
    _name = "demurrages.rates"
    _description = "delmurrages rates model"
    
    freedays =fields.Integer(string="Free days")
    lowerdays =fields.Integer(string="Lower")
    upperdays =fields.Integer(string="Upper")
    service_rate = fields.Float(string='Rate', help="MLW баталсан үнэ /НӨАТ-гүй үнэ/", ) 
    start_date =fields.Date(string="Start ", help="")
    end_date =fields.Date(string="End ", help="")
    is_ata=fields.Boolean(string="ATA")
    
    sline=fields.Many2one(comodel_name="freights.shipping.line", string="Sline")
    agent_data = fields.Many2one(comodel_name="res.partner", string="Agent", help="Захиалга өгсөн менежерийн нэр")
    taras_id = fields.Many2one('freights.taras', string='Taras')
    # country = fields.Many2one(comodel_name='res.country' , string=' Start country')
    # city=fields.Many2one( comodel_name='freights.points' , string="Start Point")
    start_point=fields.Many2one(comodel_name='freights.points' , string="Start Points")
    currency_id = fields.Many2one(comodel_name='res.currency', string="Currency", domain=['|', ('active', '=', False), ('active', '=', True)], default=lambda self: self.env.company.currency_id)
    end_point=fields.Many2one(comodel_name='freights.points' , string="End Points")
    