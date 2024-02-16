# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Ariuka. 2022-10-24

from pickletools import long1
from sre_parse import State
from unicodedata import name
from odoo import api, fields, models

class TruckingFreightPhotoModel(models.Model):
    _name = "mltrucking.freight.photo"
    _description = "Ml Trucking freight photo model"
    _rec_name = 'freight_photo'

    freight_photo = fields.Image(string = "Photo", help="зураг")
    freight_photo_desc = fields.Char(string = "Freight photo description",help = "Ачааны нэр")


    def download_photo(self): 
        return {
            'type': 'ir.actions.act_url',
            'target': 'current',
            'url': "/web/image?model=mltrucking.freight.photo&id=" + str(self.id) + "&field=freight_photo",
        }