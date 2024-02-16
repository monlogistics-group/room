# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2022-12-16

from odoo import models, fields

class WorldWideConfirmQuotation(models.Model):
    _name='worldwide.confirm.quotation'
    
    locale = fields.Many2one(string="Language",comodel_name='res.lang', domain=['|', ('active', '=', False), ('active', '=', True)])
    order=fields.Char(string='Order')
    address=fields.Char(string='Address')
    ref=fields.Char(string='ID')
    trans_type=fields.Char(string='Trans_type')
    date=fields.Char(string='date')
    consignee=fields.Char(string='Consignee')
    goods_name=fields.Char(string='Goods name')
    goods_desc=fields.Char(string='Goods desc')
    quantity=fields.Char( string='Quantity')
    receiver=fields.Char(string='Receiver')
    sender=fields.Char(string='Sender')
    condition=fields.Char(string='condition')
    estimated_time=fields.Char(string='Estimated time')
    employee=fields.Char(string='Employee')
    table_col_name_1=fields.Char(string='Table Column Name 1')
    table_col_name_2=fields.Char(string='Table Column Name 2')
    desc=fields.Char(string='Description')
    trans_broker=fields.Char(string='Transportation broker')
    name=fields.Char(string='Name')
    autograph=fields.Char(string='Autograph')
    customer=fields.Char(string='Customer')
    cust_name=fields.Char(string='Customer name')
    cust_autograph=fields.Char(string='Customer Autograph')
    title=fields.Char(string='Title')
    contract_cond_1=fields.Char(string='Contract condition 1')
    contract_cond_2=fields.Char(string='Contract condition 2')
    contract_cond_3=fields.Char(string='Contract condition 3')
    contract_cond_4=fields.Char(string='Contract condition 4')
    contract_cond_5=fields.Char(string='Contract condition 5')
    contract_cond_6=fields.Char(string='Contract condition 6')
    contract_cond_7=fields.Char(string='Contract condition 7')
    contract_cond_8=fields.Char(string='Contract condition 8')
    contract_cond_9=fields.Char(string='Contract condition 9')



