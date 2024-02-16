from odoo import models, fields
from datetime import datetime

class SocpriceRates(models.Model):
    _name = "socprice.rates"
    _description = "socprice rates model"
    
    
    taras_id = fields.Many2one('freights.taras', string='Taras')
    city=fields.Many2one(comodel_name='freights.points' ,string=" Point of Arrival")
    service_rate = fields.Float(string='Price', help="MLW баталсан үнэ /НӨАТ-гүй үнэ/", ) 
    start_date =fields.Date(string="Start (inclusive) ", help="")
    end_date =fields.Date(string="End (exclusive)", help="")
    currency_id = fields.Many2one(comodel_name='res.currency', string="Currency", domain=[('active', '=', True)], default=lambda self: self.env.company.currency_id)