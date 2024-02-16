from odoo import api, fields, models, _

class FreightTaras(models.Model):
    _name = 'freights.taras'
    _description = 'Freights Taras'

    name = fields.Char(string='Name')

    expected_volume = fields.Float(string='Expected volume (cbm)')
    expected_weight = fields.Float(string='Expected weight (Kg)')
    taras_type = fields.Char()
    
    active = fields.Boolean(default=True, string='Active')