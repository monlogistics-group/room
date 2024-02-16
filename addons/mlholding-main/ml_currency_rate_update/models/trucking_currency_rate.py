from odoo import models, fields, api

class MltruckingCurrencyRate(models.Model):
    _inherit="res.currency.rate"    
    _description='Inherited currency rate'

    not_ready_buy=fields.Float(string="Not ready to buy")
    not_ready_sell=fields.Float(string="Not ready to sell")
    ready_buy=fields.Float(string="Buy")
    ready_sell=fields.Float(string="Sell")

    currency_name = fields.Char(string='Currency', compute='get_currency_name')

    def get_currency_name(self):
        for rec in self:
            currency = self.env["res.currency"].search([("id","=", rec.currency_id.id)], limit=1)
            if currency:
                rec.currency_name = currency.name
