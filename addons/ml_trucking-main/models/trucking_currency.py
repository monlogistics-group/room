# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2023-10-20
# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo import models, fields, api
from odoo.osv import expression
import urllib.request as url_request
from bs4 import BeautifulSoup
from lxml import html

URL_MAX_SIZE = 10 * 1024 * 1024

class TruckingCurrencyModel(models.Model):
    _name = "mltrucking.currency"
    _description = "ML Trucking currency rate model"
    _rec_name = 'currency_name'
    _order = 'create_date desc'
    
    # currency_id= fields.Many2one(comodel_name="res.currency", string="Currency", help="Trucking currency", domain=['|', ('active', '=', False), ('active', '=', True)])
    currency_name = fields.Char(string='Name', index=True, required=True)
    mb_rate=fields.Float(string="Монгол банкны ханш")
    not_ready_buy=fields.Float(string="Not ready to buy")
    not_ready_sell=fields.Float(string="Not ready to sell")
    ready_buy=fields.Float(string="Buy")
    ready_sell=fields.Float(string="Sell")

    @api.model
    def get_rates_tdb(self):
        rates = 0
        url = "http://www.tdbm.mn/script.php?mod=rate&ln=mn"
        with url_request.urlopen(url) as request:
            table = BeautifulSoup(request.read(), 'html.parser')
            rows = table.findAll('tr')
            for row in rows:
                if row.find('img') != None: 
                    values = []
                    tds = row.find_all('td')
                    for td in tds:
                        values.append(td.text)
                    if len(values)>1:
                        cyrrency_name = str(values[0]).replace(' ', '').upper()
                        if cyrrency_name != "":
                            currency=self.env["res.currency"].search(['|',('active', '=', False), ('active', '=', True), ("name","=", cyrrency_name)], limit=1)
                            if(currency):
                                self.env["mltrucking.currency"].sudo().create(
                                    {
                                        'currency_name':currency.name,
                                        'mb_rate':float(str(values[1]).replace(',', '')),
                                        'not_ready_buy':float(str(values[2]).replace(',', '')),
                                        'not_ready_sell':float(str(values[3]).replace(',', '')),
                                        'ready_buy':float(str(values[4]).replace(',', '')),
                                        'ready_sell':float(str(values[5]).replace(',', '')),
                                    }
                                )
                                rates += 1
        return rates
    
    # def name_get(self):
    #     result = []
    #     for rec in self:
    #         result.append((rec.id, ("%s / %s / %s") % (rec.currency_name, str(rec.mb_rate), rec.create_date.strftime('%Y-%m-%d'))))
    #     return result
    
    # @api.model
    # def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
    #     args = list(args or [])
    #     # optimize out the default criterion of ``ilike ''`` that matches everything
    #     if not (name == '' and operator == 'ilike'):
    #         print(self)
    #         print(self.name_get)
    #         if self.currency_name:
    #             args += [(self.currency_name, operator, name)]
    #     return self._search(args, limit=limit, access_rights_uid=name_get_uid)