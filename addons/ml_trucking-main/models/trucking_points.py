# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Tuvshinbayar. 2022-12-02

from odoo import api, fields, models, _

class TruckingPoints(models.Model):
    _name = 'trucking.points'
    _description = 'Trucking Point'
    _order = 'sequence desc'
    # _rec_name = 'name' 

    sequence = fields.Integer(help="Gives the sequence order when displaying a list of records.")

    code = fields.Char(string='Code')
    name = fields.Char(string='Name')
    country_code = fields.Char(related="country.code", readonly=True, store=True)

    country = fields.Many2one('res.country', 'Country')
    state = fields.Many2one('res.country.state', 'Fed. State', domain="[('country_id', '=', country)]")

    latitude = fields.Float(string='Latitude')
    longitude = fields.Float(string='Longitude')

    border = fields.Boolean(string='Border')
    active = fields.Boolean(default=True, string='Active')

    _sql_constraints = [
        ('name_trucking_point_unique', 'unique (name, country_code)', 'Filter names must be unique'),
    ]

    def name_get(self):
        result = []
        for rec in self:
            if rec:
                result.append((rec.id, '%s/%s' % (str(rec.name), str(rec.country_code))))
        return result