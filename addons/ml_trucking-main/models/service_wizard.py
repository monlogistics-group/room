# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2022-11-15

from email.policy import default
from odoo import api, fields, models
class TestModelWizard(models.TransientModel):
    _name = 'test.model'
    _description = 'Test Model Wizard'
    
    # description=fields.Many2one(comodel_name='mltrucking.expenditure.data', string="Description")    
    # price=fields.Float(string='Price')
    current_user = fields.Many2one('res.partner','Current User', default=lambda self: self.env.user)
    parent_id=fields.Integer()
    truck_photo=fields.Many2many(comodel_name='mltrucking.freight.photo', string="Photos")
    shipment=fields.Many2one(comodel_name='mltrucking.shipment',string='Shipment')
    

    def generate_service(self):
        base_budget=self.env['mltrucking.budget'].search([('id','=',self.parent_id)])
        base_budget.update({
            'service_photos' : self.truck_photo,
            'shipment' : self.shipment.vehicle.name
        })

    