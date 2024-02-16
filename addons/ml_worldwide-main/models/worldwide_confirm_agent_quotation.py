# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2022-12-19

from odoo import models, fields

class WorldWideConfirmQuotationAgent(models.Model):
    _name = 'worldwide.confirm.agent.quotation'
    
    locale  =  fields.Many2one(string = "Language",comodel_name = 'res.lang', domain = ['|', ('active', ' = ', False), ('active', ' = ', True)])
    title = fields.Char(string = 'title')
    address = fields.Char(string = 'Address')
    ref = fields.Char(string = 'ID')
    date = fields.Char(string = 'date')
    to = fields.Char(string = 'to')
    shipper = fields.Char(string = 'Shipper')
    pickup = fields.Char(string = 'Pick up address')
    consignee = fields.Char( string = 'consignee')
    cargo = fields.Char(string = 'cargo')
    carrier = fields.Char(string = 'carrier')
    shipment_qty = fields.Char(string = 'Shipment qty')
    notice  =  fields.Char(string = 'Notice')
    purpose = fields.Char(string = 'Purpose')
    billInstruction = fields.Char(string = 'Bill Instruction')
    temp = fields.Char(string = 'Temperature')
    conf_date = fields.Char(string = 'Confirmed date')
    operationSpec = fields.Char(string = 'operationSpec')
    terms = fields.Char(string = 'Terms&conditions')
    contract_cond_1 = fields.Char(string = 'Contract condition 1')
    contract_cond_1_agent = fields.Char()
    contract_cond_2 = fields.Char(string = 'Contract condition 2')
    contract_cond_3 = fields.Char(string = 'Contract condition 3')
    contract_cond_4 = fields.Char(string = 'Contract condition 4')
    contract_cond_5 = fields.Char(string = 'Contract condition 5')
    contract_cond_6 = fields.Char(string = 'Contract condition 6')
    contract_cond_7 = fields.Char(string = 'Contract condition 7')
    contract_cond_8 = fields.Char(string = 'Contract condition 8')
    contract_cond_9 = fields.Char(string = 'Contract condition 9')
    contract_cond_10 = fields.Char(string = 'Contract condition 10')



