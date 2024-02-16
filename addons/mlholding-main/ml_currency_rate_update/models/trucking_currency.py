# -*- coding: utf-8 -*-
from odoo import models, fields, api
import random
import requests
import string
import datetime
from lxml import html
from werkzeug import urls

URL_MAX_SIZE = 10 * 1024 * 1024

class MltruckingCurrency(models.Model):
    _name = 'mlcurrency.rate.update'
    _description = 'ML currency rate update model'

    currency_rate_url = fields.Char()
    
    @api.model
    def get_rates_tdb(self):
        url = "http://www.tdbm.mn/script.php?mod=rate&ln=mn"
        if self.currency_rate_url:
            url = self.currency_rate_url
        rates = []
        try:
            head = requests.head(url, allow_redirects=True, timeout=15)
            if (
                int(head.headers.get('Content-Length', 0)) > URL_MAX_SIZE
                or
                'text/html' not in head.headers.get('Content-Type', 'text/html')
            ):
                return url
            # HTML parser can work with a part of page, so ask server to limit downloading to 50 KB
            page = requests.get(url, timeout=5, headers={"range": "bytes=0-50000"})
            table = html.fromstring(page.text.encode('utf-8'), parser=html.HTMLParser(encoding='utf-8'))
            rows = iter(table)
            rates = []
            for row in rows:
                if row.find('.//img') != None: 
                    values = [col.text for col in row]
                    values[0] = row.find('.//img').get('title')
                    rates.append(values)    

            nowdate = datetime.datetime.now()
            nowdatestr = nowdate.strftime('%Y-%m-%d')
            #base_rate = self.env["res.currency.rate"].search([("currency_id", "=", self.env["res.currency"].search([("name","=", "EUR")], limit=1).id )], limit=1).rate
            for index in rates:
                currency=self.env["res.currency"].search([("name","=", index[0].upper())], limit=1)
                if(currency):
                    # rate = self.env["res.currency.rate"].search([("currency_id", "=", currency.id )], limit=1)
                    # if rate:
                    #     # # rate.rate= index[1]
                    #     rate.not_ready_buy = float(index[2].replace(',', ''))
                    #     rate.not_ready_sell = float(index[3].replace(',', ''))
                    #     rate.ready_buy = float(index[4].replace(',', ''))
                    #     rate.ready_sell = float(index[5].replace(',', ''))
                    self.env["res.currency.rate"].sudo().create(
                        {
                            'name':nowdatestr,
                            'company_id':self.env.company.id,
                            'currency_id':currency.id,
                            'rate':1 / float(index[1].replace(',', '')),
                            'not_ready_buy':float(index[2].replace(',', '')),
                            'not_ready_sell':float(index[3].replace(',', '')),
                            'ready_buy':float(index[4].replace(',', '')),
                            'ready_sell':float(index[5].replace(',', '')),
                        }
                    )
                if index[0].upper() == "EUR":
                    print(self.env.company.currency_id)
                    currency = self.env["res.currency.rate"].search([("currency_id", "=", self.env.company.currency_id.id)], limit=1)
                    print(currency)
                    if currency:
                        currency.rate = float(index[1].replace(',', ''))
        except:
            rates = []        
        print(rates)
        return rates



