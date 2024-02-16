# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2023-01-18

from odoo import api, fields, models, _

class FreightsPaymentServicesModel(models.Model):
    _name = "freights.payment.service"
    _inherit = "freights.service"
    _description = "Worldwide freights service model"
    # _order = "shippment_ids"
    
    def _domain_shipment(self):
        arr = []
        freight = self.env["mlworldwide.freights"].browse(self.env.context.get('default_freight_id'))
        for rec in freight.freights_shipment:
            arr.append(rec.id)
        return "[('freights_id.freights_shipment.id','in', {})]".format(arr)
    
    payer_id = fields.Many2one(comodel_name="res.partner", string="Payer", help="Захиалга өгсөн менежерийн нэр",domain="[('is_company','=',True)]",)
    agent_costs_ids = fields.Many2many(comodel_name="freights.agent.cost", string="Agent costs", help="")
    shippment_ids = fields.Many2many(comodel_name="freights.shipments", string='Shipment')
    freights_id = fields.Many2one(comodel_name="mlworldwide.freights", string="Freight", ondelete='cascade')
    agent_data = fields.Many2one(comodel_name="res.partner", string="Agent", help="Захиалга өгсөн менежерийн нэр")
    package_id=fields.Many2one('freights.packages')
    # package_ids=fields.Many2one('freights.packages')
    is_ordered=fields.Boolean(string="Check")
    is_paid = fields.Boolean()
    is_invoiced = fields.Boolean()

    base_currency = fields.Many2one(comodel_name='res.currency', string="Currency", domain=[('active', '=', True)], default=lambda self: self.env.company.currency_id) #compute='_compute_currency'
    converted_rate = fields.Float(string='Rate', help="MLW үнэ /НӨАТ-гүй үнэ/", compute='compute_total_cost')
    converted_cost = fields.Float(string='Cost', help="MLW үнэ /НӨАТ-гүй үнэ/")
    converted_margin = fields.Float(string='Margin', help="MLW үнэ /НӨАТ-гүй үнэ/")
  
    def compute_total_cost(self):
        for rec in self:
            rec.converted_rate = 0
            if rec.base_currency and rec.freights_id.currency_ids:
                for exchange in rec.freights_id.currency_ids:
                    if rec.currency_id.id == exchange.currency_id.id and exchange.currency_id.id != rec.base_currency.id:
                            rec.converted_cost = round(rec.service_cost / exchange.rate, 2)
                            rec.converted_rate = round(rec.service_rate / exchange.rate, 2)
                            # rec.converted_margin = round(rec.converted_rate - rec.converted_cost, 2)
        
        

