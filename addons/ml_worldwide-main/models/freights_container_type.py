from odoo import api, fields, models, _

class FreightContainerType(models.Model):
    _name = 'freights.container.type'
    _description = 'Container Type'

    name = fields.Char(string='Name')
    active = fields.Boolean(default=True, string='Active')