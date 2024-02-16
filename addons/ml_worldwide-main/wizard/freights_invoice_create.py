# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime
from html import unescape

import requests
from odoo import api, fields, models, _
from odoo.addons.mail.wizard.mail_compose_message import _reopen
from odoo.exceptions import UserError
from datetime import timedelta, datetime, date


class FreightsInvoiceCreate(models.Model):
    _name = 'freights.invoice.create'
    _description = 'Freights Invoice Create'

    def freights_id_default(self):
        get_freight_base_id = self.env.context.get('default_freight_id')
        get_freight_base = self.env['mlworldwide.freights'].browse(get_freight_base_id)
        return get_freight_base.id

    def lang_default(self):
        get_freight_base_id = self.env.context.get('default_freight_id')
        get_freight_base = self.env['mlworldwide.freights'].browse(get_freight_base_id)
        return self.env['res.lang'].search([('code','=',get_freight_base.customer_id.lang)],limit = 1)
    
    def customer_id_default(self):
        get_freight_base_id = self.env.context.get('default_freight_id')
        get_freight_base = self.env['mlworldwide.freights'].browse(get_freight_base_id)
        return get_freight_base.customer_id.id 

    def abroad_title_default(self):
        get_freight_base_id = self.env.context.get('default_freight_id')
        get_freight_base = self.env['mlworldwide.freights'].browse(get_freight_base_id)
        return get_freight_base.freights_shipment[0].name    

    def domestic_title_default(self):
        get_freight_base_id = self.env.context.get('default_freight_id')
        get_freight_base = self.env['mlworldwide.freights'].browse(get_freight_base_id)
        return get_freight_base.freights_shipment[-1].name    

    def abroad_currency_default(self):
        get_freight_base_id = self.env.context.get('default_freight_id')
        get_freight_base = self.env['mlworldwide.freights'].browse(get_freight_base_id)
        return get_freight_base.freights_payments[0].currency_id.id    

    def freights_shipment_default(self):
        get_freight_base_id = self.env.context.get('default_freight_id')
        get_freight_base = self.env['mlworldwide.freights'].browse(get_freight_base_id)
        return get_freight_base.freights_shipment

    def freights_payments_default(self):
        get_freight_base_id = self.env.context.get('default_freight_id')
        get_freight_base = self.env['mlworldwide.freights'].browse(get_freight_base_id)
        payment_service = self.env['freights.payment.service'].search([('id', '=', -1)])
        for rec in get_freight_base.freights_payments:
            if not rec.is_invoiced:
                payment_service += rec
        return payment_service
    def _get_freights_shipment(self):
        arr = []
        freight = self.env["mlworldwide.freights"].browse(self.env.context.get('default_freight_id'))
        for rec in freight.freights_shipment:
            arr.append(rec.id)
        return "[('freights_id.freights_shipment.id','in', {})]".format(arr)
        
    freights_id = fields.Many2one(comodel_name="mlworldwide.freights", string="Freight", default=freights_id_default)
    abroad_currency = fields.Many2one(comodel_name='res.currency', domain=[('active', '=', True)],string="Abroad Currency", default=abroad_currency_default)
    domestic_currency = fields.Many2one(comodel_name='res.currency', domain=[('active', '=', True)],string="Domestic Currency", default=lambda self: self.env.company.currency_id)
    abroad_title = fields.Char(string="Abroad title", default=abroad_title_default)
    domestic_title = fields.Char(string="Domestic title", default=domestic_title_default)
    due_date = fields.Date(required=True, default=lambda self: (fields.Date.context_today(self) + timedelta(14))) #fields.Date(default=fields.Datetime.now)
    interest = fields.Float(string='Interest', default=0.30)
    lang = fields.Many2one(string="Language",comodel_name='res.lang', domain=['|', ('active', '=', False), ('active', '=', True)], default=lang_default)
    customer_id = fields.Many2one(comodel_name="res.partner", string="Payer",required=True, default=customer_id_default)
    all_shippment = fields.Boolean(default=True,)
    freights_shipment = fields.Many2many(comodel_name='freights.shipments', string="Shipments", default=freights_shipment_default, domain=_get_freights_shipment)
    freights_payments = fields.Many2many(comodel_name="freights.payment.service", string="Services", default=freights_payments_default)
    
    @api.onchange('all_shippment')
    def onchange_all_shippment(self):
        for rec in self:
            if rec.all_shippment:
                rec.freights_payments = rec.freights_id.freights_payments

    @api.onchange('freights_shipment')
    def onchange_freights_shipment(self):
        self.freights_payments = ()
        for ship in self.freights_shipment:
            for service in self.freights_id.freights_payments:
                if ship._origin.id == service.shippment_ids.id and not service.is_invoiced:
                    self.freights_payments += service
                   
    ERP_USRNAME = "Testintegration"
    ERP_PASSWORD = "Test@123"

    def send_ERP_sales(self, params):
        print("SEND Sales to ERP")
        command = "TMS_FIN_INVOICE_0011"
        body = {
            "username": self.ERP_USRNAME,
            "password": self.ERP_PASSWORD,
            "command":command,
            "parameters": params,
        }
        url = "http://erp.mlholding.mn:8080/erp-services/RestWS/runJson",
        headers = {
                "Content-Type": "application/json",
            },

        try:
            r = requests.post(url, json=body, headers=headers, timeout=65)
            r.raise_for_status()
            response = unescape(r.content.decode())
        except Exception:
            response = "timeout"
            
        return response
    
        # rp(options).then((res) => {
        #     const data: any = res.response;
        #     console.log("ressss", res);
        #     return res.response;
        # });
    

    def send_ERP_purchase(self):
        print("SEND Sales to ERP")
        command = "TMS_FIN_INVOICE_001"
        body = {
            "username": self.ERP_USRNAME,
            "password": self.ERP_PASSWORD,
            "command":command,
            "parameters": params,
        }
        url = "http://erp.mlholding.mn:8080/erp-services/RestWS/runJson",
        headers = {
                "Content-Type": "application/json",
            },

        try:
            r = requests.post(url, json=body, headers=headers, timeout=65)
            r.raise_for_status()
            response = unescape(r.content.decode())
        except Exception:
            response = "timeout"
            
        return response
    
    def create_invoice(self):
        sale_order_lines = []
        purchase_order_lines = []

        erp_sales_lanes = []
        erp_purchase_lanes = []
        for rec in self.freights_payments:
            product_id = self.env["product.product"].search([('name','=',rec.type.name)], limit=1)
            if product_id:
                if not (rec.service_desc == "" or rec.service_qty == 0 or rec.service_rate == 0 ):
                    sale_order_lines.append(
                        (
                            0, 0, 
                            {
                                'name': self.freights_id.ref_num,   #prod_name, #rec.service_desc, 
                                'product_id': product_id.id, 
                                'price_unit': rec.service_rate ,
                                'payment_ids' : rec.id,
                                'shipment_ids' : rec.shippment_ids
                            }
                            
                        ),
                    )
                    
                    purchase_order_lines.append(
                        (
                            0, 0, 
                            {
                                'name': self.freights_id.ref_num + '-' + str(self.freights_id.customer_id.id), #prod_name, #rec.service_desc, 
                                'product_id': product_id.id, 
                                'price_unit': rec.service_cost ,
                                # 'payment_ids' : rec.id,
                                'product_qty': rec.service_qty,
                            }
                            
                        ),
                    )

                    if len(product_id.taxes_id) == 0:
                        isVat = "1"
                        lineTotalVat = rec.service_rate/1.1
                    else:
                        isVat = "0"
                        lineTotalVat = ""

                    erp_sales_lanes.append( 
                        {
                            "id": "",
                            "invoiceid": "",
                            "currencyid": "",
                            "currencycode": rec.currency_id.name,
                            "qty": rec.service_qty,
                            "transactiontypeid": product_id.id, #r.transactionType,
                            "unitpricebase": rec.service_rate, #r.unitPrice,
                            "linetotalpricebase": rec.service_rate, #r.lineTotalPrice,
                            "description": self.freights_id.ref_num + '-' + str(self.freights_id.customer_id.id), #r.purpose,
                            "isVat": isVat,
                            "lineTotalVat":lineTotalVat,
                        },
                    )

                    erp_purchase_lanes.append( 
                        {
                            "id": "",
                            "invoiceid": "",
                            "currencyid": "",
                            "currencycode": rec.currency_id.name,
                            "qty": rec.service_qty,
                            "transactiontypeid": product_id.id, #r.transactionType,
                            "unitpricebase": rec.service_cost, #r.unitPrice,
                            "linetotalpricebase": rec.service_cost, #r.lineTotalPrice,
                            "description": self.freights_id.ref_num + '-' + str(self.freights_id.customer_id.id), #r.purpose,
                            "isVat": isVat,
                            "lineTotalVat":lineTotalVat,
                        },
                    )

        # TODO Purchase order line, order create.
        if len(purchase_order_lines) == 0:
            raise UserError(_("Please check service line"))
        else:
            purchase_order = self.env['purchase.order'].create({
                "partner_id": self.customer_id.id,
                "order_line": purchase_order_lines,
            })
            purchase_order.button_confirm()
        # line_name = ""
        # last_name = ""
        
        # for route in self:
        #     if line_name == "":
        #         line_name += str(route.origin_point_id.name)
        #     last_name = (route.destination_point_id.name)    
        # line_name = line_name + " - " + last_name
                               
        if len(sale_order_lines) == 0:
            raise UserError(_("Please check service line"))
         
        sale_order = self.env['sale.order'].sudo().create({
            'name': self.freights_id.ref_num,
            'partner_id': self.customer_id.id,
            'inv_line_name': self.abroad_title, 
            'order_line': sale_order_lines
        })
        sale_order.action_confirm()
        # self.is_sale_order_button = True
        #
        
        payment = self.env['sale.advance.payment.inv'].with_context({
            'active_model': 'sale.order',
            'active_ids': [sale_order.id ],
            'active_id': sale_order.id,
            'default_journal_id': self.freights_id.company_id['account_opening_journal_id'].id,
        }).create({
            'advance_payment_method': 'delivered'
        })
        payment.create_invoices()
        invoice = sale_order.invoice_ids[0]
        invoice.name = "INV "+str(self.env['account.move'].search([])[-1].id).zfill(8)
        invoice.freights_inv_id += self
        # invoice.company_id = self.company_id
        # invoice.consignee_id= self.consignee_id
        print(invoice,'--')
        for i in range(len(invoice.invoice_line_ids)):
            invoice.invoice_line_ids[i].shipment_ids = self.freights_payments[i].shippment_ids
            invoice.invoice_line_ids[i].payment_ids = self.freights_payments[i].id
            invoice.invoice_line_ids[i].account_move_id = invoice.id
        self.freights_id.invoice_id += invoice

        for payments in self.freights_payments:
            payments.is_invoiced = True

        # ERP sale order iig beldeh
        parameters = {
            "id": "",
            "booknumber": self.freights_id.ref_num + '-' + str(self.freights_id.customer_id.id),
            "bookdate": datetime.now().strftime('%YYYY-%MM-%DD') ,
            "customerid": "",
            "duedate": self.due_date.strftime('%YYYY-%MM-%DD') ,
            "description": self.freights_id.ref_num + '-' + str(self.freights_id.customer_id.id),
            "booktypeid": "",
            "departmentid": "",
            "customercode": self.customer_id.id,
            "departmentcode": sale_order.id,
            "ordernumber": sale_order.id,
            "suppliername": self.freights_id.shipper_info,
            "shipmentnumber": len(self.freights_id.freights_shipment),
            "shipmentqty": len(self.freights_id.freights_shipment),
            "shipmentdescription": self.freights_id.shipper_detail,
            "objectid": "",
            "isimport": "1",
            "fininvoicedtl":erp_sales_lanes,
        }
        
        # erpresult = self.send_ERP_sales(parameters)
        ## TODO erp gees irsen resultiiyg hadgalj abana 

        parameters = {
            "id": "",
            "booknumber": invoice.name,
            "bookdate": datetime.now().strftime('%YYYY-%MM-%DD'),
            "customerid": "",
            "duedate": self.due_date.strftime('%YYYY-%MM-%DD'),
            "description": self.freights_id.ref_num + '-' + str(self.freights_id.customer_id.id),
            "booktypeid": "",
            "departmentid": "",
            "customercode": self.freights_id.customer_id.id,  #customerCode,
            "departmentcode": self.freights_id.customer_id.id, #data.details.departmentcode,
            "ordernumber": purchase_order.id,
            "suppliername": self.freights_id.shipper_info, #data.details.shipper || "undefined",
            "shipmentnumber": len(self.freights_id.freights_shipment), #data.details.shipmentNumber,
            "shipmentqty": len(self.freights_id.freights_shipment), #data.details.shipmentQty || "undefined",
            "shipmentdescription": self.freights_id.shipper_detail, #data.details.cargo,
            "objectid": "",
            "isimport": "1",
            "fininvoicedtl":erp_purchase_lanes,
        }

        # erpresult = self.send_ERP_purchase(parameters)
        ## TODO erp gees irsen resultiiyg hadgalj abana 

        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': invoice.get_portal_url(),
        }



