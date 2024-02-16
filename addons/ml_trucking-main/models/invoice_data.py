# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Ariuka. 2022-11-22

from odoo import api, fields, models

class InvoiceDataModel(models.Model):
    _name = "mltrucking.invoice.data"
    _description = "ML Trucking invoice data model"
    
    info_name=fields.Char(string="Invoice")
    inv_name=fields.Char(string = "PLANTIFF")
    organi_name=fields.Char(string="NAME OF THE ORGANIZATION")
    payer_number=fields.Char(string="payer number")
    inv_add=fields.Char(string="ADDRESS")
    inv_phone=fields.Char(string="PHONE")
    payer_email =fields.Char(string="Email")
    payment_per=fields.Char(string="PAYMENT PERIOD")
    bnk_name=fields.Char(string="BANK TYPE")
    bnk_nmbr=fields.Char(string="BANK OF NUMBER")
    payer=fields.Char(string="PAYER")
    payer_name=fields.Char(string="NAME OF THE ORGANIZATION")
    payer_add=fields.Char(string="RAYER ADDRESS")
    contract_number=fields.Char(string="CONTRACT NUMBER")
    inv_date=fields.Char(string="VALID DATE")
    invoi_date=fields.Char(string="INVOICE DATE")
    serv_desc=fields.Char(string="Description")
    serv_name=fields.Char(string="SERVICE NAME")
    serv_qty=fields.Char(string="QUANTITY")
    serv_cost=fields.Char(string="N vne ")
    serv_tot=fields.Char(string="SERVICE TOTAL")
    direct_name=fields.Char(string="Director Name")
    senior_name=fields.Char(string="Senior A Name")
    director_acc= fields.Char(string="Executive Director")
    senior_acc= fields.Char(string="Senior Accountant")
    locale = fields.Many2one(string="Language",comodel_name='res.lang', domain=['|', ('active', '=', False), ('active', '=', True)])