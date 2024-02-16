# -*- coding: utf-8 -*-
# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-12-02

from odoo import models, fields

class ResCompany(models.Model):
    _inherit = "res.company"

    other_logos= fields.Many2many(comodel_name="mlfreights.photos", string="Other logos",) 
    
    bank_info_title=fields.Char(string = "Bank info title" )
    bank_info_l1=fields.Char(string="Bank Name")
    bank_info_l2=fields.Char(string="Address")
    bank_info_l3=fields.Char(string="Swift Code")
    bank_info_l4=fields.Char(string="Account Name")

class TruckingFreightPhotoModel(models.Model):
    _name = "mlfreights.photos"
    _description = "Ml photo model"

    freight_photo = fields.Image(string = "Photo", help="зураг")
   
    def download_photo(self): 
        return {
            'type': 'ir.actions.act_url',
            'target': 'current',
            'url': "/web/image?model=mltrucking.freight.photo&id=" + str(self.id) + "&field=freight_photo",
        }