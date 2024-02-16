# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Ariuka. 2022-12-02

from odoo import api, fields, models

class SaleOrderQuotationDataModel(models.Model):
    _name = "mltrucking.sale.order.quotation.data"
    _description = "ML Trucking sale order quoatation model"
    
    ship_conf=fields.Char(string="SHIPMENT CONFIRMATION")
    title_name=fields.Char(string="REFERENCE")
    ship_type=fields.Char(string="SHIPMENT TYPE")
    ship_date=fields.Char(string="DATE")
    ship_to=fields.Char(string="TO")
    package_name=fields.Char(string="PACKAGE NAME")
    package_desc=fields.Char(string="PACKAGE DESCRIPTION")
    package_qty=fields.Char(string="PACKAGE QTY")
    package_vendor=fields.Char(string="PACKAGE VENDOR")
    package_con=fields.Char(string="Package vn")
    ekso_condi=fields.Char(string="CONDITION")
    package_valid_until=fields.Char(string="VALID UNTIL")
    package_rt_name=fields.Char(string="pacake route manager")
    condi_route=fields.Char(string="CONDITION&ROUTE")
    package_cost=fields.Char(string="Confirmed cost")
    border=fields.Char(string="BORDER")
    transport_agent=fields.Char(string="TRANSPORT AGENT")
    costumer_name=fields.Char(string="COSTUMER NAME")
    agent_name=fields.Char(string="NAME :KHOS ")
    cos_name=fields.Char(string="NAME : Lhag")
    sign=fields.Char(string="SIGN")
    condi_text=fields.Char(string="CONDITION TEXT")
    condi_texts=fields.Char(string="CONDITION TEXT")
    locale = fields.Many2one(string="Language",comodel_name='res.lang', domain=['|', ('active', '=', False), ('active', '=', True)])
    
    
    
    # shipper=fields.Char(string="SHIPPER")
    # pick_up=fields.Char(string="PICK UP ADDRESS")
    # pick_consignee=fields.Char(string="CONSIGNEE")
    # cargo_name=fields.Char(string="CARGO")
    # ship_qty=fields.Char(string="SHIPMENT QTY")
    # bill_instruction=fields.Char(string="BILL INSTRUCTION")
    # purpose=fields.Char(string="PURPOSE")
    # conf_rate=fields.Char(string="CONFIRMED RATE")
    # oper_spec=fields.Char(string="OPERATION SPECIALIST")
    # teams_condi=fields.Char(string="TEAMS & CONDITIONS")
    
    