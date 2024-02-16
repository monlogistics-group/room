# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-12-02

from odoo import api, fields, models

class FreightsLocationModel(models.Model):
    _name = "freights.location"
    _description = "ML Worldwide freights Location model"
    _rec_name = 'location_date'
    _order = 'location_date asc'

    location_latitude = fields.Float('Geo Latitude', digits=(10, 7))
    location_longitude = fields.Float('Geo Longitude', digits=(10, 7))
    location_altitude = fields.Float('Geo Altitude', digits=(10, 7))

    freights_id = fields.Many2one('mlworldwide.freights', 'Freight', tracking=True, )

    location_date = fields.Datetime(string="Location time", help="Ачаа огноо")