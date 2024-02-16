# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2022-11-02

from datetime import date
from email.policy import default
from odoo import api, fields, models

class TruckingPackage(models.Model):
    _name = "mltrucking.package"
    _description = "Ml Truckin package model"
    
    consignee=fields.Many2one(string='Consignee',comodel_name='res.partner')
    weight=fields.Integer(string="Weight(KG)")
    quantity=fields.Integer(string="Quantity")
    dangerousGoods=fields.Many2one(comodel_name='mltrucking.package.data', string='Dangerous Goods')
    name=fields.Char(string="Name", default='freight')
    temp=fields.Char(string="Temperature")
    note=fields.Char(string="Note")
    shipment=fields.Many2one(string='Shipment', comodel_name='fleet.vehicle')
    length= fields.Integer(string = "Length",help = "Ачааны урт")
    width = fields.Integer(string = "Width",help = "Ачааны өргөн")
    height = fields.Integer(string = "Height",help = "Ачааны өндөр")
    color=fields.Integer(compute='calc_color')

    def calc_color(self):
        self.color=2

    def action_get_each_document(self):
        parent_id=self.env['mltrucking.base'].browse(self.env.context.get('default_base_id'))
        report = self.env['ir.actions.report']._get_report_from_name('ml_trucking.mltrucking_each_document')
        report.report_type = 'qweb-pdf'
        active_doc=parent_id.truck_package.search([('id','=',self.id)])
        parent_id.active_docs=active_doc

        pdf = report.report_action(parent_id, config = False)
        return pdf  
    