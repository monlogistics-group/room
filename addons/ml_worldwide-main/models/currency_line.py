

from odoo import api, fields, models, _

class CurrencyLine(models.Model):
    _name = "currency.line"
    _description = "Currency Line"

    buy = fields.Float('buy', default=0.0)
    sell = fields.Float('sell', default=0.0)
    rate = fields.Float('rate', default=0.0)
    
    freight_id = fields.Many2one('mlworldwide.freights', 'Freight',readonly=True, ondelete='cascade')
    freight_quotation_id = fields.Many2one('freights.quotations', 'Quotation', readonly=True, ondelete='cascade')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True)
