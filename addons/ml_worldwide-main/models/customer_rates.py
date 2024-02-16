# from odoo import models, fields
from datetime import datetime
from odoo import api, fields, models, _

class CustomersRates(models.Model):
    _name = "customers.rates"
    _description = "customers rates model"
       
    start_date =fields.Date(string="Start ", help="")
    end_date =fields.Date(string="End ", help="")
    service_data=fields.Char(string="Service")
    service_data_eng = fields.Char()
    package_data=fields.Char(string="Package")
    to_data=fields.Float(string="To")
    from_data=fields.Float(string="From")
    type_data=fields.Char(string="Type")
    cost_data=fields.Float(string="Cost")
    is_last=fields.Boolean( default =True )

    currency_id = fields.Many2one(comodel_name='res.currency', string="Currency",domain=[('active', '=', True)] ,default=lambda self: self.env.company.currency_id)
    point_data=fields.Many2one(comodel_name='freights.terminal' ,string="Terminal")

    @api.model
    def create(self,values):
        a = self.env["customers.rates"].search([("service_data","=",values['service_data'])])
        for rec in a:
            rec.is_last = False
        return super(CustomersRates, self).create(values)