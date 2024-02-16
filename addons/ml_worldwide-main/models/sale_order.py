# -*- coding: utf-8 -*-
# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-12-02

from odoo import models, fields,api
class SaleOrder(models.Model):
    _inherit = "sale.order"

    inv_line_name=fields.Char(string="Invoice line name")

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    state_freight = fields.Char(string="Freight Invoice State")
    freights_inv_id = fields.Many2many(comodel_name='freights.invoice.create', string="Freight inv id")
    sub_state = fields.Selection(selection=[('approved', 'approved'), ('sent', "sent"), ('paid', 'paid')],default='approved')
    lang = fields.Many2one(string="Language",comodel_name='res.lang', domain=['|', ('active', '=', False), ('active', '=', True)])
    # description = fields.Char()

    def _get_name_invoice_report(self):
        self.ensure_one()
        if self.freights_inv_id:
            return 'ml_worldwide-main.mlworldwide_invoice_template'
        return super()._get_name_invoice_report()
    
    def get_amount_str(self, amount):
        print(amount)
        return "get_amount_str"

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    shipment_ids = fields.Many2many('freights.shipments')
    payment_ids = fields.Many2one('freights.payment.service')


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    shipment_ids = fields.Many2many('freights.shipments')
    payment_ids = fields.Many2one('freights.payment.service')
    account_move_id = fields.Many2one('account.move')

    def delete_item(self):
        self.payment_ids.is_invoiced = False
        account_move = self.env['account.move'].search([('id', '=', self.account_move_id.id)])
        account_move.invoice_line_ids = [(3, self.id, 0)]

class PackagesPopUp(models.Model):
    _name = 'packages.pop.up'
    
    def _default_selected_packages(self):
        get_package_ids = self.env.context.get('default_selected_package_ids')
        package_id = self.env['freights.packages'].search([('id', '=', -1)])
        for rec in get_package_ids:
            package_id += self.env['freights.packages'].search([('id', '=', rec)])
        return package_id
        
    date = fields.Datetime()
    selected_packages = fields.Many2many('freights.packages', default=_default_selected_packages)
    # todo
    # container move bolon shipment arrived bolgono
    def confirm(self):
        for rec in self.selected_packages:
            if rec.state_id == 'on-going':
                rec.state_id = 'arrived'
        
            # if rec.number_id.shipment_type_id.name == 'Container':
            #     container_move = self.env['freights.container.movement'].search([('id', '=', rec.number_id.container_type_id.id)])
            #     container_move.

