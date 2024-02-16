# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Ariuka. 2022-10-24

from odoo import api, fields, models
from datetime import datetime

class QuotationDataModel(models.Model):
    _name = "mlworldwide.quotation.data"
    _description = "ML Worldwide quotation data model"

    def _lang_get(self):
        langs = self.env['res.lang'].get_installed()
        return langs

    quote_lang = fields.Selection(string="Language", selection=_lang_get, default ='en_US', domain=['|', ('active', '=', False), ('active', '=', True)])
    title_name=fields.Char(string = "RATE QUOTATION",help = "Тээврийн үнийн санал")
    worldwide_reference=fields.Char(string="REFERENCE")
    worldwide_date=fields.Char(string="DATE")
    worldwide_valit_until=fields.Char(string="VALIT UNTIL")
    worldwide_to=fields.Char(string="TO")
    worldwide_detail=fields.Char(string="Cargo Detail")
    worldwide_transit_time=fields.Char(string="ESTIMATED TRANSIT TIME")
    worldwide_incoterms=fields.Char(string="INCOTERMS")
    worldwide_routes=fields.Char(string="ROUTES")
    worldwide_rate=fields.Char(string="RATE")
    worldwide_include=fields.Char(string="ABOVE RATE INCLUDED BELOW CHARGES")
    worldwide_not_include=fields.Char(string="ABOVE RATE NOT INCLUDED BELOW CHARGES")
    worldwide_remark=fields.Char(string="Remark")
    worldwide_border=fields.Char(string="Border")
    worldwide_remark_body=fields.Html(widget="html", string="Text")