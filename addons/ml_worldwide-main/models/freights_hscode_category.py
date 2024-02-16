from odoo import api, fields, models, _


class FreightsHscodeCategory(models.Model):
    _name = 'freights.hscode.category'
    _description = 'cargo Category'

    code = fields.Char(string='Code')
    name = fields.Char(string='Name')
    
    active = fields.Boolean(default=True, string='Active')