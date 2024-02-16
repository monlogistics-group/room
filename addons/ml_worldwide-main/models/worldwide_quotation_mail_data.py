# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2022-11-10

from datetime import date
from email.policy import default
from odoo import api, fields, models

class WorldWideQuotationMail(models.Model):
    _name = "mlworldwide.quotation.mail"
    _description = "Ml Wordlwide mail model"

    def _lang_get(self):
        langs = self.env['res.lang'].get_installed()
        return langs

    greeting=fields.Char(string="Greeting")
    description=fields.Char(string='Description')
    route=fields.Char(string='Route')
    footer=fields.Char(string='footer')
    table_number=fields.Char(string='Table Number')
    table_type=fields.Char(string='Table Type')
    table_id=fields.Char(string='Table ID')
    table_information=fields.Char(string='Table Information')
    border=fields.Char(string="Border")
    price=fields.Char(string='Table price')
    table_estimated_time=fields.Char(string='Estimated Time')
    def _lang_get(self):
        langs = self.env['res.lang'].get_installed()
        return langs

    locale = fields.Many2one(string="Language",comodel_name='res.lang', domain=['|', ('active', '=', False), ('active', '=', True)])
    
    air_warning=fields.Text(string="AIR freight warning text")