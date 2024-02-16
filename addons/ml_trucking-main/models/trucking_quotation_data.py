# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Ariuka. 2022-10-24

from odoo import api, fields, models
from datetime import datetime,timedelta

class QuotationDataModel(models.Model):
    _name = "mltrucking.quotation.data"
    _description = "ML Trucking quotation data model"
    
    title_name=fields.Char(string = "RATE QUOTATION",help = "Тээврийн үнийн санал")
    truck_reference=fields.Char(string="REFERENCE")
    truck_date=fields.Char(string="DATE")
    truck_valit_until=fields.Char(string="VALIT UNTIL")
    truck_to=fields.Char(string="TO")
    truck_detail=fields.Char(string="Cargo Detail")
    truck_transit_time=fields.Char(string="ESTIMATED TRANSIT TIME")
    truck_incoterms=fields.Char(string="INCOTERMS")
    truck_routes=fields.Char(string="ROUTES")
    truck_service_name=fields.Char(string="SERVICE NAME")
    truck_rate=fields.Char(string="RATE")
    truck_include=fields.Char(string="ABOVE RATE INCLUDED BELOW CHARGES")
    truck_not_include=fields.Char(string="ABOVE RATE NOT INCLUDED BELOW CHARGES")
    truck_remark=fields.Char(string="Remark")
    truck_remark_body=fields.Char(string="Text")
    
    locale = fields.Many2one(string="Language",comodel_name='res.lang', domain=['|', ('active', '=', False), ('active', '=', True)])
    
    
    # def _lang_get(self):
    #         langs = self.env['res.lang'].get_installed()
            
    #         return langs
    # locale = fields.Selection(string="Language", selection=_lang_get, default = "default", domain=['|', ('active', '=', False), ('active', '=', True)])
    
    @api.onchange('date_begin', 'date_end','date_diff')
    def calculate_date(self):
        if self.date_begin and self.date_end:
            d1=datetime.strptime(str(self.date_begin),'%Y-%m-%d %H:%M:%S') 
            d2=datetime.strptime(str(self.date_end),'%Y-%m-%d %H:%M:%S')
            d3=d2-d1
            self.date_diff=str(d3.days)
          