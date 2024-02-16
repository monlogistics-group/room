# -*- coding: utf-8 -*-
# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-11-10

from odoo import models, fields

class ResCompany(models.Model):
    _inherit = "res.company"

    other_logos=fields.Many2many(comodel_name='mltrucking.freight.photo', string="Other logos")
    law_text=fields.Char(string="Text Of Law")
    step_sign=fields.Image( string="Stamp")
    bank_name=fields.Char(string="Bank Type Name")
    bank_number=fields.Integer(string="Bank Number")
    bank_info_l1=fields.Char(string="bank_info_l1")
    bank_info_l2=fields.Char(string="bank_info_l2")
    bank_info_l3=fields.Char(string="bank_info_l3")
    bank_info_l4=fields.Char(string="bank_info_l4")
    bank_title=fields.Char(string = "Bank info title" )
    
    