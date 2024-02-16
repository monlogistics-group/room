# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2023-04-05

from odoo import api, Command, fields, models, modules, _,tools

class FreightPhotoModel(models.Model):
    _name = "mlworldwide.freight.photo"
    _rec_name = 'freight_photo'

    freight_photo = fields.Image(string = "Photo", help="зураг")
