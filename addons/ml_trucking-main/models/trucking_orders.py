# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2022-11-02

from datetime import date
from email.policy import default
from odoo import api, fields, models

class TruckingOrders(models.Model):
    _name = "mltrucking.order"
    _description = "Ml Truckin order model"
    
    description=fields.Char('description')
    volume=fields.Integer(string="Volume (CBM)")
    gweight=fields.Integer(string="Gross Weight (KG)")
    quantity=fields.Integer(string="Quantity")
    package=fields.Char(string="Package")
    operation=fields.Char(string="Operation")
    
    def _get_user(self):
        print("get_agent")    
        # return self.env.user

    def write(self,vals):
        self.env['mltrucking.route'].create({
            'origin': self.description,
        })
        return super(TruckingOrders, self).write(vals)
