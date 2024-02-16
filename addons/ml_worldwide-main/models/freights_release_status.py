from odoo import api, fields, models, _

class FreightPackageStatus(models.Model):
    _name = 'freights.release.status'
    _description = 'Package Status'

    # Original bill, Hold, Releasable
    name = fields.Char(string='Name')
    active = fields.Boolean(default=True, string='Active')