# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2023-5-10

from email.policy import default
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

class ConfirmWizard(models.TransientModel):
    _name = 'quotation.confirm.wizard'
    
    quotation = fields.Many2one('freights.quotations')
    shipment_qty = fields.Integer(string='Shipment Qty')
    ett_max = fields.Integer(string='Ett max')
    is_inspection = fields.Boolean()
    recipients = fields.Many2many('res.partner')
    pic = fields.Many2one('hr.employee')
    consignee = fields.Many2one('res.partner')
    agent_contact_mails = fields.Many2many('quotation.agents.mail')
    text = fields.Char(string="Margin")

    def confirm(self):
        if self.quotation.total_rate == 0:
            raise ValidationError('You must fill rate fields')

        if self.quotation.state_id != 'confirmed':
            self.quotation.state_id = 'confirmed'

        self.quotation.confirm_active = False
        self.quotation.freights_id.sudo().route_shipment_boolean = True
        self.quotation.freights_id.sudo().state_id='confirmed'
        self.quotation.freights_id.state_buttons = False
        self.quotation.freights_id.ett_max = self.ett_max
        self.quotation.freights_id.is_inspection = self.is_inspection
        # self.quotation.freights_id.has_tir = self.
        self.quotation.freights_id.recipients = self.recipients
        self.quotation.freights_id.shipment_qty = self.shipment_qty

        for curr in self.quotation.currency_ids:
            if curr.freight_quotation_id.id ==  self.quotation.id:
                curr.write({
                    'freight_id' : self.quotation.freights_id.id
                })

        arr = []
        for contributor in self.quotation.freights_id.contributor_ids:
            arr.append(contributor.employee)
        self.quotation.freights_id.state_checker = True
        confirm_quot_customer = self.env.ref('ml_worldwide-main.mlworlwide_confirm_quotation_email')
        check = False
        if self.pic.id:
            if self.pic not in arr:
                employee_role = self.env['freights.employee.role'].search([])
                for rec in employee_role:
                    if self.pic.id == rec.employee.id:
                        check = True
                        self.quotation.freights_id.contributor_ids += rec
                if not check:                        
                    contributor = self.env['freights.employee.role'].sudo().create({
                        'employee' : self.pic.id,
                        'role_name' : ''
                    })
                    self.quotation.freights_id.contributor_ids += contributor

        operation = []
        for op in self.quotation.freights_id.contributor_ids:
            for role in op.employee.user_id:
                if role.has_group('ml_worldwide-main.group_mlworldwide_operation'):
                    operation.append(op.employee.work_email)

        for rec in self.agent_contact_mails:
            contacts = []
            for mail in rec.contacts:
                contacts.append(mail.email)
            mails=','.join([str(elem) for elem in contacts])
            if len(operation) > 0:
                op_cc=','.join([str(elem) for elem in operation])
                confirm_quot_customer.write({'email_to': mails,'auto_delete': False, 'email_cc' : op_cc})
            else:
                confirm_quot_customer.write({'email_to': mails,'auto_delete': False})

            try:
                confirm_quot_customer.send_mail(
                    rec.service_id.id, force_send=True
                )
            except UserError as e:
                raise ValidationError('Can`t sent confirm email. %s' % e.args[0])


        shipment_order_email = []
        if self.quotation.freights_id.customer_id.company_type == "company":
            for child in self.quotation.freights_id.customer_id.child_ids:
                shipment_order_email.append(child.email)
        else:
            shipment_order_email.append(self.quotation.freights_id.customer_id.email)
        if len(shipment_order_email)>0:
            mails=','.join([str(elem) for elem in shipment_order_email])
            operation.append(self.quotation.freights_id.employee.work_email)
            op_cc=','.join([str(elem) for elem in operation])
            template_rec = self.env.ref('ml_worldwide-main.mlworlwide_confirm_agent_quotation_email')
            template_rec.write({'email_to': mails,'auto_delete': False, 'email_cc' : op_cc})
            template_rec.send_mail(
                self.quotation.id, force_send=True) 


        points = []
        for service in self.quotation.service_ids:
            for rec in service.type:
                if rec.name == 'Freight cost' or rec.name == 'Package':
                    if service.service_from:
                        points.append(service.service_from.id)
                    if service.service_to:
                        points.append(service.service_to.id)
        unique_list = []
        [unique_list.append(x) for x in points if x not in unique_list]
        arr = []
        if self.quotation.freights_id.origin_point_id:
            arr.append(self.quotation.freights_id.origin_point_id.id)
        if self.quotation.freights_id.destination_point_id:
            arr.append(self.quotation.freights_id.destination_point_id.id)
        [arr.append(x) for x in unique_list if x not in arr]
        i = 0
        for rec in arr:
            route=self.env['freights.route'].create({
                'sequence': i,
                'freights_id' : self.quotation.freights_id.id,
                'point' : rec
            })
            self.quotation.freights_id.sudo().freights_route += route
            i += 1
        # package = self.env['freights.packages'].create({
        #     'name' : self.quotation.freights_id.notes,
        #     'consignee_id' : self.quotation.freights_id.customer_id.id,
        #     'package_qty': self.quotation.freights_id.package_qty,
        #     'number_id' : shipment.id
        # }) 
        # shipment.write({
        #     'shipment_packages' : package
        # })
        # if self.quotation.freights_id.volume:
        #     package.write({
        #         'volume' : self.quotation.freights_id.volume
        #     })
        # if self.quotation.freights_id.gross:
        #     package.write({
        #         'volume' : self.quotation.freights_id.volume
        #     })
        self.quotation.freights_id.sudo().ordered_freights_type = self.quotation.freights_type_ids
        # self.quotation.create_payments(self.quotation.freights_id, self.quotation.service_ids)        
        # self.quotation.freights_id.shipment_calc()
        
        for i in range(self.shipment_qty):
            print(i,'oh yeag---------------')
            shipment_qty = self.env['freights.shipments'].create({
                        'name' : 'Temp %d' % (len(self.quotation.freights_id.freights_shipment)+1),
                        'freights_id' : self.quotation.freights_id.id,
                    })
            print(shipment_qty,'shipment_qty---------------')
            self.quotation.freights_id.freights_shipment += shipment_qty
        for shipment in self.quotation.freights_id.freights_shipment:
            for package in shipment.shipment_packages:
                package.consignee_id = self.consignee
