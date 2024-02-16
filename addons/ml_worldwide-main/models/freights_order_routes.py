from odoo import api, fields, models, _

class FreightOrderRuotes(models.Model):
    _name = 'freights.order.routes'
    _description = 'Routes'

    name = fields.Char(string='Name')
    
    route_point_ids = fields.Many2many(comodel_name='freights.points', string="Routes")