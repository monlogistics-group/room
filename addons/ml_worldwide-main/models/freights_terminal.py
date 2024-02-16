import logging
from odoo import api, fields, models, _



class FreightTerminal(models.Model):
    _name = 'freights.terminal'
    _description = 'Freight Terminal'

    active = fields.Boolean(default=True, string='Active')

    name = fields.Char(string='Name')
    street = fields.Char()
    city = fields.Char()
    zip = fields.Char()
    
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one("res.country", string='Country', ondelete='restrict')
