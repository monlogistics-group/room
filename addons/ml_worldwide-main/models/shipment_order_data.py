from odoo import api, fields, models

class ShipmentOrderDataModel(models.Model):
    _name = "shipment.order.data"
    _description = "Shipment order"
    
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
    agent_name=fields.Char(string="NAME :Bayarkhuu ")
    cos_name=fields.Char(string="NAME : Uyanga")
    sign=fields.Char(string="SIGN")
    condi_text=fields.Char(string="CONDITION TEXT")
    condi_texts=fields.Char(string="CONDITION TEXT")
    notice=fields.Char(string="NOTICE")
    temp_deg=fields.Char(string="TEMPERATURE DEGREES")
    locale = fields.Many2one(string="Language",comodel_name='res.lang', domain=['|', ('active', '=', False), ('active', '=', True)])
    