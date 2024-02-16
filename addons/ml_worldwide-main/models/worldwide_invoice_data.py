# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Ariuka. 2022-11-22

from odoo import api, fields, models

class WorldWideInvoiceDataModel(models.Model):
    _name = "mlworldwide.invoice.data"
    _description = "ML WorldWide invoice data model"
    
    invoice_address=fields.Char(string="ADDRESS")
    invoice_phone=fields.Char(string="PHONE")

    invoice_title=fields.Char(string="Invoice")
    invoice_num=fields.Char(string="Invoice number")
    invoice_date=fields.Char(string="INVOICE DATE")
    invoice_duedate=fields.Char(string="VALID DATE")
    payer=fields.Char(string="PAYER")
    payer_number=fields.Char(string="payer number")
    freights_num=fields.Char(string="freights number")
    shipment_name_fcl=fields.Char(string="Shipment number")
    shipment_name_lcl=fields.Char(string="Shipment number")
    shipment_name_ftl=fields.Char(string="Shipment number")
    shipment_name_ltl=fields.Char(string="Shipment number")
    shipment_name_air=fields.Char(string="Shipment number")
    shipment_name_train=fields.Char(string="Shipment number")
    shipment_name_wgn=fields.Char(string="Shipment number")
    shipment_name_multimodal=fields.Char(string="Shipment number")

    cargo_name=fields.Char(string="Cargo name")
    package_qty=fields.Char(string="Package quantity")
    shipper_name=fields.Char(string="Shpper")

    table_head_num=fields.Char(string="Number")
    table_head_desc=fields.Char(string="Description")
    table_head_qty=fields.Char(string="Quantity")
    table_head_price=fields.Char(string="Price")
    table_head_subtotal=fields.Char(string="Total price")
    total_price=fields.Char(string="Total price")
    total_payment=fields.Char()

    abroad_title=fields.Char(string = "Abroad")
    domestic_title=fields.Char(string="Doemestic")
    note_msg=fields.Char(string="Note msg")
    notice_text = fields.Char()
    direct_name=fields.Char(string="Job title")
    nuot = fields.Char(string="VAT")
    bank_name = fields.Char()
    mnt = fields.Char()
    usd = fields.Char()
    eur = fields.Char()
    cny = fields.Char()
    rub = fields.Char()
    
    lang = fields.Many2one(string="Language",comodel_name='res.lang', domain=['|', ('active', '=', False), ('active', '=', True)])