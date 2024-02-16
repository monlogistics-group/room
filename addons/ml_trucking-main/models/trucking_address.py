# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2022-10-26

from inspect import modulesbyfile

from odoo import api, fields, models

class TruckingAddress(models.Model):
    _name="mltrucking.address"

    _description = "Ml Trucking address"
    
    contact_name = fields.Char(string="Name")
    country = fields.Many2one(string="Country",comodel_name="res.country",)
    state=fields.Many2many(comodel_name="res.country.state")
    city = fields.Char(string="City")
    street1=fields.Char()
    phone=fields.Integer(string="Phone number")
    street=fields.Many2one(string='', comodel_name="res.country")
    state_id=fields.Many2one(string='', comodel_name="res.country")
    zip=fields.Integer('')
    country_id=fields.Integer('')
    email=fields.Char(string="Mail")
    # street2
    # phone
    # mobile   
    # email 
    # description 