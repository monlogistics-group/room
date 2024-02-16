from odoo import models, fields
from datetime import datetime

class FreightsDemurragesRates(models.Model):
    _name = "freight.demurrages.rates"
    _inherit = "demurrages.rates"
    _description = "freight delmurrages rates model"
    
    freight_id = fields.Many2one('mlworldwide.freights', 'Freight', ondelete='cascade')
    freight_quotation_id = fields.Many2one('freights.quotations', 'Quotation', ondelete='cascade')
    