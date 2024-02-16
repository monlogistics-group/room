# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2022-10-27

from datetime import date
from email.policy import default
from odoo import api, fields, models

class TruckingRoute(models.Model):
    _name = "mltrucking.route"
    _description = "Ml Truckin route model"
    _order = 'vehicle'
    
    sequence = fields.Integer()
    description=fields.Char('description')
    type=fields.Selection([('pickup','Pickup'),('oncarriage','On Carriage'),('precarriage','Pre Carriage'),('delivery','Delivery')], default="pickup")
    transport=fields.Selection([('air', 'Air'),('ocean', 'Ocean'),('land', 'Land')], default="air")
    date=fields.Date(string='Date')
    trucker=fields.Char(string="Trucker")
    truckerNo=fields.Integer(string='Trucker No')
    
    origin_point = fields.Many2one(comodel_name='trucking.points', string='Origin')
    dist_point = fields.Many2one(comodel_name='trucking.points', string='Destination')
    # origin=fields.Many2one(string='Origin',comodel_name='res.country')
    # origin_related=fields.Integer(related="origin.id")
    # origin_city=fields.Many2one(string='City', comodel_name='res.country.state', placeholder="City")
    # origin_city_related=fields.Integer(related="origin_city.id")
    # destination=fields.Many2one(placeholder='County',string='Destination',comodel_name='res.country')
    # destination_related=fields.Integer(related="destination.id")
    # dest_city=fields.Many2one(placeholder='City', comodel_name='res.country.state', string='City')
    # dest_city_related=fields.Integer(related="dest_city.id")

    vehicle=fields.Many2one(comodel_name='fleet.vehicle')
    ETD=fields.Date(string='ETD')
    ETA=fields.Date(string='ETA')
    ATD=fields.Date(string='ATD')
    ATA=fields.Date(string='ATA')
    # a=fields.Char(default='a')
    # b=fields.Char(default='b')
