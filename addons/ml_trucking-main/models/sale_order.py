# -*- coding: utf-8 -*-
# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-11-10

from odoo import api, models, fields

class SaleOrder(models.Model):
    _inherit = "sale.order"

    inv_line_name=fields.Char(string="Invoice line name")
    base_id=fields.Integer()


class AccountMove(models.Model):
    _inherit = 'account.move'
    trucking_id = fields.Many2one(comodel_name='mltrucking.base', string="Trucking id", help = "Trucking ID")
    # company_id = fields.Many2one(comodel_name='mltrucking.base')
    # vendor_id= fields.Many2one(comodel_name='mltrucking.base', string="Trucking consignee id", help = "Trucking")

    def _get_name_invoice_report(self):
        self.ensure_one()
        if self.trucking_id:
            return 'ml_trucking.mltrucking_invoice_template'
        return super()._get_name_invoice_report()


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.onchange('lst_price')
    def onchange_product_lst_price(self):
        for product in self:
            product.lst_price = product.lst_price * 1.1

