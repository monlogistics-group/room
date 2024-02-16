# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-12-02

from selenium.webdriver.common.by import By
import os
import base64
from email.policy import default
from odoo import api, fields, models, _, Command
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import json

class WorldwideFreigthsModel(models.Model):
    _name = "mlworldwide.freights"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "ML Worldwide freigths model"
    _rec_name = 'ref_num'

    def _get_default_state(self):
        state = self.env.ref('ml_worldwide-main.freight_state_new_request', raise_if_not_found=False)
        return state if state and state.id else False
    
    def _get_user(self):
        return self.env.user

    def _get_employee_id(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        return employee_rec.id    

    def _get_insurance(self):
        if self.is_prepaid:
            return False
        return True

    # customer_id = fields.Many2one(comodel_name="res.partner", string="Customer", help="Захиалагч",required=True, track_visibility='onchange' ,domain="[('is_company','=',False)]")
    # customer_id = fields.Many2one(comodel_name="res.partner", string="Customer", help="Захиалагч",required=True, track_visibility='onchange' ,domain="[('parent_id','!=',False)]")
    customer_id = fields.Many2one(comodel_name="res.partner", string="Customer", help="Захиалагч",required=True, track_visibility='onchange',domain="[('parent_id','!=',False)]")
    # origin term and origin point ,domain="[('is_company','=',False)]"
    # origin_term = fields.Many2one('freights.terms', 'Origin term')
    origin_term = fields.Many2one('origin.incoterms', 'Origin term',required=True, track_visibility='onchange')
    freight_id = fields.Many2one('freights.container.movement')
    incoterm_uses_address = fields.Char(related="origin_term.code", readonly=True, store=True)
    origin_point_id = fields.Many2one(comodel_name='freights.points', string='Origin Point',required=True, track_visibility='onchange')
    # destination term and destination point
    destination_term = fields.Many2one('destination.incoterms', 'Destination term',required=True, track_visibility='onchange')
    destination_point_id = fields.Many2one( 'freights.points', string='Destination Point',required=True, track_visibility='onchange')
    delivery_uses_address = fields.Char(related="destination_term.code", readonly=True, store=True)
    # cargo code
    hscode_category_id = fields.Many2one('freights.hscode.category', string='Cargo Category',required=True, track_visibility='onchange')
    ref_num = fields.Char(string='Reference', default=lambda self: self.env["mlworldwide.freights"].compute_name(),) 
    is_show_details = fields.Boolean('View details', default = False)
    is_accountant = fields.Boolean('View details', default = False, compute='_compute_is_accountant')
    # added by tuvshin  
    is_prepaid = fields.Boolean('Prepaid', default=False, track_visibility='onchange')
    is_export = fields.Boolean('Export', default=False, track_visibility='onchange')
    has_insurance = fields.Boolean('Has Insurance', default=_get_insurance, track_visibility='onchange')
    dangerous_goods = fields.Boolean('Is Dangerous', track_visibility='onchange')
   
    # to do add language customer
    pickup_address = fields.Text('PickUp Address', track_visibility='onchange')
    delivery_address = fields.Text('Delivery Address', track_visibility='onchange')

    # shipper info
    shipper_info = fields.Char('Shipper', track_visibility='onchange')
    shipper_detail = fields.Text('Shipper Contact Details', track_visibility='onchange')

    notes = fields.Char('Cargo name', track_visibility='onchange', required=True,)
    hs_code = fields.Char('HS Code', track_visibility='onchange')
    agent_inquiry_mail_subject=fields.Char(  'Mail subject' ,)
    # FCL LTL etc
    freigths_type = fields.Many2many(comodel_name="freights.type", string="Type", help="Freights type", required = True, track_visibility='onchange') 
    ordered_freights_type = fields.Many2one(comodel_name="freights.type", string="Type", help="Order Freights type", track_visibility='onchange') 
    ett_max = fields.Integer()
    is_inspection = fields.Boolean()
    has_tir = fields.Boolean()
    recipients= fields.Many2many('res.partner')
    
    show_tara = fields.Boolean()
    
    taras_id = fields.Many2many('freights.taras', string='Taras', track_visibility='onchange')
    # shipping_line_id = fields.Many2one('shipping.line', 'Shipping Line')
    package_qty = fields.Integer(string='Package Qty', track_visibility='onchange', default=1, required = True)
    volume = fields.Float(string='Volume(cbm)', track_visibility='onchange')
    gross = fields.Float(string='Gross(kg)', track_visibility='onchange')

    shipment_qty = fields.Integer(string='Shipment Qty', track_visibility='onchange', default=1, )
    ref = fields.Boolean('Ref', track_visibility='onchange')
    terminal_id = fields.Many2one('freights.terminal', 'Terminal',required=True, track_visibility='onchange')
    temperature = fields.Char('Temperature', track_visibility='onchange')
    wagon_type_id = fields.Many2one('freights.wagon.type', 'WGN type', track_visibility='onchange')
    truck_type_id = fields.Many2one('freights.truck.type', 'Truck type', track_visibility='onchange')
    show_wgn = fields.Boolean()
    show_truck = fields.Boolean()
    show_volgross = fields.Boolean(default=False)
    show_hscode = fields.Boolean(default=False)
    show_remark = fields.Boolean(default=False)
    
    invoice_count = fields.Integer(string='Invoice Count' , compute='_get_invoiced')
    service_count = fields.Integer(string='Service', help='Not invoiced service Count' , compute='_get_service_count')
    
    fclroute_ids = fields.Many2many('freights.route.category', string='FCL Routes', store=True, track_visibility='onchange')
    
    user_id = fields.Many2one(comodel_name="res.users", string="User", default=_get_user, help="Захиалга өгсөн менежерийн нэр", required=True, readonly=True)
    employee = fields.Many2one('hr.employee', string="Created by", default=_get_employee_id, readonly=True, required=True, help="Захиалга өгсөн менежерийн нэр")
    # employee_ids = fields.Many2many('hr.employee',)

    contributor_ids = fields.Many2many('freights.employee.role', string="Participants", readonly=False, help="Хамтрагч менежерийн нэр", track_visibility='onchange')


    local_remark=fields.Text(string='Local remark', track_visibility='onchange')
    notice=fields.Html(string='Notice', track_visibility='onchange')
    remark=fields.Text(string='SC & SO Notice', track_visibility='onchange')
    attachement_ids = fields.Many2many(comodel_name='ir.attachment', string='File', track_visibility='onchange')
    is_lmao = fields.Boolean()
    state_id = fields.Selection(selection=[
            ('created', 'Created'),
            ('quotation', 'Quotation'),
            ('re-inquiry', 'Re-inquiry'),
            ('confirmed', 'Confirmed'),
            ('on-going', 'On going'),
            ('arrived', 'Arrived'),
            ('released', 'Released'),
            ('closed', 'Closed'),
            ('cancelled', 'Cancelled'),
        ], default='created', tracking=True)

    company_id = fields.Many2one('res.company', string='Company',  readonly=True, default=lambda self: self.env.company)

    freights_quotations = fields.One2many("freights.quotations","freights_id", track_visibility='always') #readonly=True, store=True
    freights_inquiries = fields.One2many("freights.agent.inquiry","freights_id", track_visibility='always') #readonly=True, store=True
    freights_route = fields.One2many('freights.route',"freights_id", track_visibility='always')
    freights_shipment = fields.One2many('freights.shipments',"freights_id", ttrack_visibility='always')
    freights_shipment_remark = fields.One2many('freights.shipments.remark',"freights_id", track_visibility='onchange')
    
    freights_routes_shipment = fields.One2many('freights.route.shipment',"freights_id", track_visibility='always')
    lost_reason=fields.Many2one(comodel_name="mlworldwide.reason", string='Lost Reason', track_visibility='always')
    # state_id_cancel=fields.Integer()
    freights_payments = fields.One2many("freights.payment.service", "freights_id", track_visibility='always')
    freights_agent_review = fields.One2many("freights.agent.review", "freight_id", track_visibility='always')
    
    freights_channel_id = fields.Many2one(comodel_name='mail.channel', track_visibility='always')
    
    route_shipment_boolean = fields.Boolean()
    show_quotation = fields.Boolean()
    
     #  Ene boolean iig true bol active teever false bol canceldsen teever
    is_active_freights = fields.Boolean(string="Check is active service", default=True)
    active = fields.Boolean(default=True, help="Set active to false to hide the Freights without removing it.")
    is_done_freights = fields.Boolean(string="Check is active service", default=False)
    is_assigned_freights = fields.Boolean(string="Check is assign freights", default=False, compute='compute_assign_freights')
    ctx = fields.Char()

    cancel_active = fields.Boolean('Active_Cancel', default=True, tracking=True)
    state_buttons = fields.Boolean(default = True)
    lost_reason=fields.Many2one(comodel_name="mlworldwide.reason", string='Lost Reason', tracking=True )
    note=fields.Char()
    invoice_id = fields.Many2many('account.move', string="Sale order", ondelete="cascade", readonly=False, )
    
    state_checker = fields.Boolean()
    date_store = fields.Char(compute='_compute_is_expired')
    is_expired = fields.Boolean()
    is_send_email = fields.Boolean(string="Email send", default=False)
    state_click = fields.Boolean(default=False)

    currency_ids = fields.One2many('currency.line', 'freight_id', 'Currency set')
    # def get_filtered_records(self):
    #     return self.env['mlworldwide.freights'].search([], limit=1)
    
    def freight_quotation(self):
        self.state_id = 'quotation'
        self.show_quotation = True

    def freight_reinquiry(self):
        self.state_id = 're-inquiry'

    def freight_closed(self):
        self.state_id = 'closed'
        checkin_review = True
        for rec in self:
            for review in rec.freights_agent_review:
                if review.rate=='0' or review.review=="":
                    checkin_review = False
        if checkin_review:
            self.feedback_email()
        else:
            raise ValidationError('Agent not reviewed.')

    def _compute_is_expired(self):
        if self.date_store:
            print(self.date_store,'-------')
            d1=datetime.strptime(str(fields.Datetime.from_string(fields.Datetime.from_string(self.date_store).date())),'%Y-%m-%d') 
            d2=datetime.strptime(str(datetime.now().strftime('%Y-%m-%d')),'%Y-%m-%d')
            d3=d2-d1
            date_diff=str(d3.days)
            if date_diff > 0:
                for record in self:
                    record.note = 'Expired'

    def compute_is_details_show(self):
        print("compute_is_details_show")
        self.is_show_details = not self.is_show_details

    def toggle_active(self):
        self.state_id = 'cancelled'
        self.cancel_active = True
    
    def action_send(self):
        self.ensure_one()
        # freight_id=self.env.context.get("default_freight_id")
        template_id = self.env.ref('ml_worldwide-main.route_template').id
        
        template = self.env['mail.template'].browse(template_id)
        template_rec = self.env.ref('ml_worldwide-main.route_template')
        
        for rec in self.customer_id:
            arr = []
            for child in rec.child_ids:
                arr.append(child.email)
            mails=','.join([str(elem) for elem in arr])
            template_rec.write({
                'email_to' : mails
            })
            
        print(self.ids[0],'----------------------')
        ctx = {
            'default_model': 'mlworldwide.freights',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            # 'defualt_freight_id':freight_id
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }
    

    def action_send_all(self):
        self.ensure_one()
        # freight_id=self.env.context.get("default_freight_id")
        template_id = self.env.ref('ml_worldwide-main.email_all_template_name').id
        
        template = self.env['mail.template'].browse(template_id)
        template_rec = self.env.ref('ml_worldwide-main.email_all_template_name')
        
        for rec in self.customer_id:
            arr = []
            for child in rec.child_ids:
                arr.append(child.email)
            mails=','.join([str(elem) for elem in arr])
            template_rec.write({
                'email_to' : mails
            })
            
        print(self.ids[0],'----------------------')
        ctx = {
            'default_model': 'mlworldwide.freights',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            # 'defualt_freight_id':freight_id
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }
    
    def _get_invoiced(self):
        for order in self:
            order.invoice_count = len(order.invoice_id)
    
    def _get_service_count(self):        
        for order in self:
            invoiced = 0
            for service in order.freights_payments:
                if not service.is_invoiced:
                    invoiced += 1
            order.service_count = invoiced

    def add_records_to_payment(self):

        wizard = self.env['add.record.to.payments'].create({
            'freights_id' : self.id,
            'shippment_ids' : self.freights_shipment
        })
        return {
            'name': ('Add Records'),
            'type': 'ir.actions.act_window',
            'res_model': 'add.record.to.payments',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new'
        }

    def search_create_wizard(self):
        wizard = self.env['freight.search.wizard'].create({
            'country' : self.origin_point_id.country.id,
            'helper_id' : self.id
        })
        return {
            'name': ('Filter conditions'),
            'type': 'ir.actions.act_window',
            'res_model': 'freight.search.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new'
        }
        
    def compute_assign_freights(self):
        for recs in self:
            check_in = True
            if len(recs.freigths_type) == 0:
                    check_in = False
            else:
                cnt = 0
                for rec in recs.freigths_type:
                    if len(recs.contributor_ids) == 0:
                        check_in = True
                    else:
                        for emp in recs.contributor_ids:
                            print(rec.type_name, emp.role_name)
                            if rec.type_name == emp.role_name:
                                cnt += 1
                if cnt >= len(recs.freigths_type):
                    check_in = False
            recs.is_assigned_freights = check_in
            
    # User ni accountant baih ued REMARK iin door invoice_id nuudiig kharuulana busad ued hidden baian 
    def _compute_is_accountant(self):
        if self.env.user.id:
            if self.user_has_groups('ml_worldwide-main.group_mlworldwide_accountant'):
                for rec in self:
                    rec.is_accountant = True
            else:
                self.is_accountant = False
            # employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
            # print(employee_rec.user_groups,'==========employee_rec.user_groups')
            # if not employee_rec.user_groups:
            #     self.is_accountant = False
            # for user_group in employee_rec.user_groups:
            #     if "accountant" in user_group.name.lower():
            #         for rec in self:
            #             rec.is_accountant = True
            #     else:
            #         self.is_accountant = False
    
    def get_accountant(self, uid):
        if self.env.user.id:
            employee_rec = self.env['hr.employee'].search([('user_id', '=', uid.id)], limit=1)
            print("get_accountant")
            print(uid)
            print(self.env)
            print(self.env.user)
            print(self.env.user.id)
            print(employee_rec.id)
            if employee_rec.id:
                return employee_rec
            else:
                return {}

    # Read buh shaardlaga hangsan recordiig butsaana
    def read(self, fields=None, load='_classic_read'):
        records = super(WorldwideFreigthsModel, self).read(fields=fields, load=load)
        print(records,"=============records")
        return records

    def compute_name(self):
        code = str(self.env['ir.sequence'].next_by_code('mlworldwide.freights.sequence'))
        tmp = base64.b64encode(str.encode(code)).decode('utf-8')
        name = "F" + str(fields.Datetime.now().year)[2:] + '' + tmp.upper()
        return name

    @api.model
    def create(self, values):
        origin_point = self.env['freights.points'].search([('id', '=', values['origin_point_id'])], limit=1)
        origin_point.sequence += 1
        dest_point = self.env['freights.points'].search([('id', '=', values['destination_point_id'])], limit=1)
        dest_point.sequence += 1
        code = str(self.env['ir.sequence'].next_by_code('mlworldwide.freights.sequence'))
        tmp = base64.b64encode(str.encode(code)).decode('utf-8')
        name = "F" + str(fields.Datetime.now().year)[2:] + '' + tmp.upper()
        values["ref_num"] = name
        if 'show_volgross' in values:
            if values["show_volgross"]:
                if 'volume' in values:
                    if values["volume"] == 0:
                        raise UserError("Volume value not zero")
                if 'gross' in values:
                    if values["gross"] == 0:
                        raise UserError("Gross value not zero") 
        if 'dangerous_goods' in values:
            if values["dangerous_goods"]:
                if values['attachement_ids'].length == 0:
                    raise UserError("Must be file attach when dangerous goods ") 
        
        chnl = self.env['mail.channel'].search([('name','=', name)])
        if not chnl:
            channel = self.env['mail.channel'].sudo().create({
                'name': '' + name,
                'channel_partner_ids': [(4, self.env['res.users'].browse(self.env.user.id).partner_id.id)]
            })
            values['freights_channel_id'] = channel.id
        templates = super(WorldwideFreigthsModel, self).create(values)
        # fix attachment ownership
        for template in templates:
            if template.attachement_ids:
                template.attachement_ids.write({'res_model': self._name, 'res_id': template.id})
        return templates

    def copy(self, default=None):
        self.ensure_one()
        code = str(self.env['ir.sequence'].next_by_code('mlworldwide.freights.sequence'))
        tmp = base64.b64encode(str.encode(code)).decode('utf-8')
        name = "C" + str(fields.Datetime.now().year)[2:] + '' + tmp.upper()
        default = dict(default or {}, ref_num=name)
        chnl = self.env['mail.channel'].search([('name','=', name)])
        if not chnl:
            channel = self.env['mail.channel'].sudo().create({
                'name': '' + name,
                'channel_partner_ids': [(4, self.env['res.users'].browse(self.env.user.id).partner_id.id)]
            })
            default = dict(default or {}, freights_channel_id=channel.id)
        return super(WorldwideFreigthsModel, self).copy(default)

    def write(self, vals):
        
        # if self.freights_routes_shipment:
        #     if 'freights_routes_shipment' in vals and not self.freights_routes_shipment[0].atd_date:
        #         is_ongoing = False
        #         for recs in vals['freights_routes_shipment']:
        #             if recs[2]:
        #                 if 'atd_date' in recs[2]:
        #                     if recs[1] == self.freights_routes_shipment[0].id and recs[2]['atd_date']:
        #                         is_ongoing = True
        #         if is_ongoing:
        #             print("********************************************* ONGOING *********************************************")
        #             self.state_id = 'on-going'
        # TODO create Channel, Topic vals["ref_num"]
        # create Firebase Topic Freight name subscribe topic
        chnl = self.env['mail.channel'].search([('name','=',self.ref_num)])
        if not chnl:
            channel = self.env['mail.channel'].sudo().create({
                'name': '' + self.ref_num,
                'channel_partner_ids': [(4, self.env['res.users'].browse(self.env.user.id).partner_id.id)]
            })
            
            for ps in self.contributor_ids:
                if ps.employee.user_partner_id:
                    channel.sudo().channel_partner_ids += ps.employee.user_partner_id

            vals['freights_channel_id'] = channel.id

        result = super(WorldwideFreigthsModel, self).write(vals)     
        # self.shipment_calc()           
        print(result,' Step 1  =================')
        # if result.state_id == 'confirmed':
        #     result.cancel_active = True
        msg = ""
        for record in self:
            if record.dangerous_goods or record.show_volgross:
                if record.volume == 0:
                    msg += "Volume value must be not zero\n"
                if record.gross == 0:
                    msg += "Gross value must be not zero\n"

            if  record.dangerous_goods:
                if len(record.attachement_ids) == 0:
                    msg += "File attachment must be not empty\n"
            if  record.dangerous_goods or 'WGN' in record.freigths_type:
                if record.hs_code == False:
                    msg += "HS code value must be not empty\n"
        print('Step 2  =================')
        if msg != "":
            print(msg)
            raise ValidationError(msg)
        print(result,' Step 3  =================')
        return result
    
    def freight_cancel(self):
        lost_wizard = self.env['mlworldwide.reason.remark'].sudo().create({
            'base_id': self.id
        })
        
        return {
            'name': ('Cancel reason'),
            'type': 'ir.actions.act_window',
            'res_model': 'mlworldwide.reason.remark',
            'view_mode': 'form',
            'res_id': lost_wizard.id,
            'target': 'new'
        }
        print(self.freight_lost , '=============================')
   
        
    def action_assign_freights(self):
        # print(self.employee_ids)
        print(self.freigths_type.ids)
        action = {
            'name': 'Freight types',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'freights.type.assign',
            'view_id': self.env.ref('ml_worldwide-main.freights_type_assign_wizard_form').id,
            'target':"new",
            'context': {'default_freigths_type': self.freigths_type.ids, "default_freight_id": self.id},
        }

        action.update({
            'domain': [('freigths_type', 'not in', self.freigths_type)],
        })

        return action
    key = 'ml_worldwide-main'
    
    def get_base_url(self):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        if not 'localhost' in base_url:
            if 'http://' in base_url:
                base_url = base_url.replace('http://', 'https://')
        base_url = base_url + '/feedback?freight_id=' + str(self.id) + '&agent_id='
        return base_url

    def feedback_email(self):
        self.ensure_one()
        self.env['freights.client.feedback'].sudo().create({
            'agent_id' : self.customer_id.id,
            'rate' : 0,
            'expire_date': datetime.now(),
            'freight_id' : self.id
        })

        customers = self.env['res.partner'].search([('id', '=', self.customer_id.id)],limit=1)
        print(customers,'customers--------')
        emails_arr=[]
        for child in customers.child_ids:
            emails_arr.append(child.email)
        
        emails=','.join([str(el) for el in emails_arr])
        print(emails,'=')
        template=self.env.ref('ml_worldwide-main.mlworldwide_feedback_email_template')
        template.write({
            'subject' : "Feed back",
            'email_from' : "info.mlholding.mn",
            'email_to' : emails
        })
        
        template.send_mail(
            self.id, force_send=True #, raise_exception=True
        )

        # ctx = {
        #     'default_model': 'mlworldwide.freights',
        #     'default_res_id': self.id,
        #     'default_use_template': bool(template.id),
        #     'default_template_id': template.id,
        #     'default_composition_mode': 'comment',
        #     'force_email': True,
        # }
        # return {
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'form',
        #     'res_model': 'mail.compose.message',
        #     'views': [(False, 'form')],
        #     'view_id': False,
        #     'target': 'new',
        #     'context': ctx,
        # }  
        # 
        #  
        # self.assertEqual(str(activity_id.date_deadline), '2022-12-31')
 
    def send_truck(self):
        template_id = self.env.ref('ml_worldwide-main.send_truck').id
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
            
        ctx = {
            'default_model': 'mlworldwide.freights',
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True,
        }
        self.is_send_email = True
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    # def convert_order(self):

    #     starttime =datetime.now() + timedelta(minutes=1)  #).strftime('%Y-%m-%d %H:%M:%S')
        
    #     # dates  = self.get_due_date(starttime, 16)

     

    #     partners = self.env['hr.employee'].search([], limit=3)

    #     # self.send_notification(partners, dates['start_date'], dates['end_date'], "title", "body", "notification")

    #     return ""
    #     endtime = (datetime.now() + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
    #     self.create_event_activity("meeting", starttime, endtime, "TEST Meeting khiine shuu")
        
    #     print("convert_order", self.ref_num)
        
    #     # notification = ('<div class="mlworldwide.freights"><a href="#" class="o_redirect" data-oe-id="%s">#%s</a></div>') % (str(self.id), self.ref_num,)
    #     # self.freights_channel_id.message_post(body='Freights: ' + notification, message_type='notification')
    #     # emp = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
    #     # if emp:
    #     #     self.env["res.company"].send_topic_message("MLW Freights", 'Freights: ' + notification, self.ref_num)

    #     # return ""

    #     print(self.freights_channel_id)

    #     return ""


    #     print("convert_order")
    #     print(int(float(datetime.now().strftime('%s.%f')) * 1e3))
    #     code = str(self.env['ir.sequence'].next_by_code('mlworldwide.freights.sequence'))
    #     print(code)
    #     print(base64.b64encode(str.encode(code)).decode('utf-8'))
    #     # return  ""

    #     starttime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #     endtime = (datetime.now() + timedelta(hours=16)).strftime('%Y-%m-%d %H:%M:%S')
    #     print("meeting", starttime, endtime, "Meeting khiine shuu")
    #     self.create_event_activity("meeting", starttime, endtime, "Meeting khiine shuu")

    #     self.employee.with_user(self.employee.id).message_post(
    #         author_id=41, body="body", message_type='comment', content_subtype='plaintext'
    #     )

    #     # return  ""

         
    #     self.env['mail.message'].create(
    #         {
    #             'email_from': self.env.user.partner_id.email, # add the sender email
    #             'author_id': self.env.user.partner_id.id, # add the creator id
    #             'model': 'mail.channel', # model should be mail.channel
    #             'subtype_id': self.env.ref('mail.mt_comment').id, #Leave this as it is
    #             'body': "Body of the message", # here add the message body
    #             # s'channel_ids': [(4, 130)], # This is the channel where you want to send the message and all the users of this channel will receive message
    #             'res_id': 130, #self.env.ref('ml_worldwide-main.channel_accountant_group').id, # here add the channel you created.
    #         }
    #     )

    #     print("NOTIFY")

    #     if self.customer_id:
    #         notification_ids = [(0, 0,
    #                             {
    #                                 'res_partner_id': 41,
    #                                 'notification_type': 'inbox'
    #                             }
    #                             )]

    #     notification = {
    #         'type': 'ir.actions.client',
    #         'tag': 'display_notification',
    #         'params': {
    #         'title': _('Warning'),
    #         'message': 'You cannot do this action now',
    #         'sticky': True,
    #         }
    #     }

    #     # return notification
    #     self.env['mail.message'].create({
    #         'message_type': "notification",
    #         'body': "Your Body",
    #         'subject': "Your Subject",
    #         'partner_ids': [(4, self.customer_id.id, 41)],
    #         'model': self._name,
    #         'res_id': self.id,
    #         'notification_ids': notification_ids,
    #         'author_id': self.env.user.partner_id and self.env.user.partner_id.id
    #     })
    

    #     """ holiday ehelsen bn uu ?"""
    #     holidays = self.env["hr.leave"].search(['&',('date_from', '>=', start_date),('date_from', '<=', end_date)])
    #     # if not holidays:
    #     holidays += self.env["hr.leave"].search(['&',('date_from', '<=', start_date),('date_to', '>=', end_date)])
    #         # if not holidays:
    #     holidays += self.env["hr.leave"].search(['&',('date_from', '<=', start_date),('date_to', '>=', start_date)])
    #             # if not holidays:
    #     holidays += self.env["hr.leave"].search(['&',('date_from', '>=', start_date),('date_to', '<=', end_date)])
                    
    #     total_day = 0

    #     for days in holidays:
    #         stat_name = days.holiday_status_id.name.lower()
    #         if "holiday" in stat_name:
    #             total_day += (days.date_to - days.date_from).days


    #     end_date = end_date + timedelta(days=total_day)
        
    #     return {
    #         'start_date' : self.timezonetoUTC8(start_date),
    #         'end_date' : self.timezonetoUTC8(end_date)
    #     }
    
    def send_notification(self, partners, start_date, end_date, title, body, type):
        starttime =start_date.strftime('%Y-%m-%d %H:%M:%S')
        endtime = end_date.strftime('%Y-%m-%d %H:%M:%S')
        if type == "meeting":
            self.create_event_activity(starttime, endtime, title, body, type)
        elif type == "notification":
            return self.create_notification(title, body, type) 
        elif type == "message":
            self.create_message(partners, body)
        elif type == "all":
            self.create_event_activity(starttime, endtime, title, body, type)
            self.create_message(partners, body)  
            return self.create_notification(title, body, type)   

    def action_get_quotation(self):
        print("action_get_quotation")
        print(self.id)
        print(self._origin.id)
        print(self._origin)

    def create_quotation(self):
        quote = self.env["freights.quotations"].sudo().create({
            'freights_id': self.id,
            'freights_type_ids': '',
            'service_ids': self.freights_service,
            'quote_cost': self.total_cost
        })
        # print(self.freights_service,'---------kkk')
        # self.action_assign_freights()
        self.freights_quotations += quote

    @api.onchange('freights_payments')
    def _onchange_freights_payments(self):
        for rec in self:
            for freights_payment in rec.freights_payments:
                in_reviewed = False
                for review in rec.freights_agent_review:
                    if review.agent_id == freights_payment.agent_id:
                        in_reviewed = True
                if in_reviewed == False:
                    new_review = self.env['freights.agent.review'].sudo().create({
                        'agent_id': freights_payment.agent_id.id,
                        'freight_id': rec.id
                    })
                    rec.freights_agent_review += new_review
                    freights_payment.agent_id.freights_agent_review += new_review
    
    @api.onchange('freights_quotations')
    def _onchange_quotation(self):
        arr = []
        # if len(self.freights_quotations) > 0:
        #     employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        #     for user in employee_rec.user_groups:
        #         arr.append(user.name.lower())
            # if 'pd' not in arr:
            #     raise ValidationError("You don't have permission to do this action")
           
    @api.onchange('is_prepaid')
    def _onchange_prepaid(self):
        self.has_insurance = not self.is_prepaid

    @api.onchange('taras_id')
    def _onchange_taras_id(self):
        if self._origin.id:
            froom = ""
            for types in self.env['mlworldwide.freights'].browse(self._origin.id).taras_id:
                froom += types.name + ","
            too = ""    
            for line in self:
                for types in line.taras_id:
                    too += types.name + ","
            print(froom, too)
            self.env['mlworldwide.freights'].browse(self._origin.id).message_post(body = '''<ul class="o_Message_trackingValues"><li>
                                                        <div class="o_Message_trackingValue" role="group">
                                                            <div class="o_Message_trackingValueFieldName o_Message_trackingValueItem">Type: </div>
                                                            <div class="o_Message_trackingValueOldValue o_Message_trackingValueItem">%s</div>
                                                            <div class="o_Message_trackingValueSeparator o_Message_trackingValueItem fa fa-long-arrow-right" title="Changed" role="img"/>
                                                            <div class="o_Message_trackingValueOldValue o_Message_trackingValueItem">%s</div>
                                                        </div>
                                                    </li>
                                                </ul>''' % (froom, too))
    
    @api.onchange('fclroute_ids')
    def _onchange_fclroute_ids(self):
        if self._origin.id:
            froom = ""
            for types in self.env['mlworldwide.freights'].browse(self._origin.id).fclroute_ids:
                froom += types.name + ","
            too = ""    
            for line in self:
                for types in line.fclroute_ids:
                    too += types.name + ","

            self.env['mlworldwide.freights'].browse(self._origin.id).message_post(body = '''<ul class="o_Message_trackingValues"><li>
                                                        <div class="o_Message_trackingValue" role="group">
                                                            <div class="o_Message_trackingValueFieldName o_Message_trackingValueItem">Type: </div>
                                                            <div class="o_Message_trackingValueOldValue o_Message_trackingValueItem">%s</div>
                                                            <div class="o_Message_trackingValueSeparator o_Message_trackingValueItem fa fa-long-arrow-right" title="Changed" role="img"/>
                                                            <div class="o_Message_trackingValueOldValue o_Message_trackingValueItem">%s</div>
                                                        </div>
                                                    </li>
                                                </ul>''' % (froom, too))


    @api.onchange('freigths_type')
    def _onchange_freights_type(self):
        print("_onchange_freights_type", self._origin.id)
        if self._origin.id:
            froom = ""
            for types in self.env['mlworldwide.freights'].browse(self._origin.id).freigths_type:
                froom += types.type_name + ","
            too = ""    
            for line in self:
                for types in line.freigths_type:
                    too += types.type_name + ","
                print(line.freigths_type)
            
            self.env['mlworldwide.freights'].browse(self._origin.id).message_post(body = '''<ul class="o_Message_trackingValues"><li>
                                                        <div class="o_Message_trackingValue" role="group">
                                                            <div class="o_Message_trackingValueFieldName o_Message_trackingValueItem">Type: </div>
                                                            <div class="o_Message_trackingValueOldValue o_Message_trackingValueItem">%s</div>
                                                            <div class="o_Message_trackingValueSeparator o_Message_trackingValueItem fa fa-long-arrow-right" title="Changed" role="img"/>
                                                            <div class="o_Message_trackingValueOldValue o_Message_trackingValueItem">%s</div>
                                                        </div>
                                                    </li>
                                                </ul>''' % (froom, too))
        # self.sudo().message_post(body = "Freights type changed", subject =" self.freigths_type.type_name")
        res = False
        wgn = False
        truck = False
        volgross = False
        hscode = False
        remarl = False
        for record in self.freigths_type:
            typname = str(record.type_name).upper()
            if typname == "FCL":
                res = True
                # print(self.shipment_qty)
                # for rec in range(self.shipment_qty):
                #     shipment=self.env['freights.shipments'].create({
                #         'name': rec
                #     })
                #     self.freights_shipment += shipment
            if typname == "WGN":
                wgn = True
            if typname == "LCL" or typname == "LTL" or typname == "AIR" or typname == "TRAIN" or typname == "WGN" or typname == "MULTIMODAL":
                volgross = True
            if typname == "WGN":
                hscode = True
            if typname == "MULTIMODAL":
                remarl = True
            if typname == "FTL":
                truck = True
        self.show_tara = res
        self.show_wgn = wgn
        self.show_volgross = volgross
        self.show_hscode = hscode
        self.show_remark = remarl
        self.show_truck = truck
    
    @api.onchange('state_id')
    def _onchange_state_id(self):
        print(self.state_id,'-======================')
        # self.state_click = True
        if self.state_id == 'closed':
            checkin_review = True
            for rec in self:
                for review in rec.freights_agent_review:
                    if review.rate=='0' or review.review=="":
                        checkin_review = False
            if checkin_review:
                self.feedback_email()
            else:
                raise ValidationError('Agent not reviewed.')
        print(self.state_id,'-----------',self._origin.state_id)
        if self.state_id == 'quotation':
            self.state_click = False
        if self._origin.state_id == 'quotation':
            self.state_click = True
            print('hah')
            if self.state_id == 're-inquiry':
                self.state_click = False

        if self._origin.state_id == 're-inquiry':
            if self.state_id == 'created':
                self.state_click = True
            if self.state_id == 'quotation':
                self.state_click = False

        if self._origin.state_id == 'confirmed':
            if self.state_id == 'created' or self.state_id == 'quotation' or self.state_id == 're-inquiry':
                self.state_click = True

        if self.state_id == 'confirmed':
            self.state_checker = True
        else:
            self.state_checker = False
        # if self.state_id != self._origin.state_id:
        #     if self.state_id == 'on-going' or self.state_id == 'released':
        #         self.state_click = True
            # sh
                # raise ValidationError('This status is automatically change')
        if self.state_id == "quotation":
            self.show_quotation = True
        if self.state_id == 'confirmed':
            self.route_shipment_boolean = True
    
    # @api.onchange('state_id')
    # def _onchange_state_id(self):
    #     if self.state_id == 'closed':
    #         checkin_review = True
    #         for rec in self:
    #             for review in rec.freights_agent_review:
    #                 if review.rate=='0' or review.review=="":
    #                     checkin_review = False
    #         if checkin_review:
    #             self.feedback_email()
    #         else:
    #             raise ValidationError('Agent not reviewed.')

    #     if self._origin.state_id == 'confirmed':
    #         if self.state_id == 'created' or self.state_id == 'quotation' or self.state_id == 're-inquiry':
    #             raise ValidationError("Its not possible")

    #     if self.state_id == 'confirmed':
            
    #         self.state_checker = True
    #     if self.state_id != self._origin.state_id:
    #         if self.state_id == 'on-going' or self.state_id == 'released':
    #             raise ValidationError('This status is automatically change')
    #     if self.state_id == "quotation":
    #         self.show_quotation = True
    #     if self.state_id == 'confirmed':
    #         self.route_shipment_boolean = True


    @api.onchange('freights_route')
    def _onchange_freights_route(self):
        self.shipment_calc()

    # @api.onchange('freights_shipment')
    # def _onchange_freights_shipment(self):
    #     print('asdjoaisjdlasjdklasjdlkasjdlkajsdkl')

    
    def action_view_services(self):
        invoices = self.mapped('freights_payments')
        action = self.env["ir.actions.actions"]._for_xml_id("ml_worldwide-main.freights_payment_service_action")
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('ml_worldwide-main.freights_payment_service_form_view').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_move_type': 'out_invoice',
        }
        if len(self) == 1:
            context.update({
                'default_partner_id': self.customer_id.id,
                # 'default_partner_shipping_id': self.partner_shipping_id.id,
                'default_invoice_payment_term_id': self.customer_id.property_payment_term_id.id or self.env['account.move'].default_get(['invoice_payment_term_id']).get('invoice_payment_term_id'),
                'default_invoice_origin': self.ref_num,
                'default_user_id': self.user_id.id,
            })
        action['context'] = context
        return action
    
    def action_view_invoice(self):
        invoices = self.mapped('invoice_id')
        print(invoices,'=-=======================')
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_move_type': 'out_invoice',
        }
        if len(self) == 1:
            context.update({
                'default_partner_id': self.customer_id.id,
                # 'default_partner_shipping_id': self.partner_shipping_id.id,
                'default_invoice_payment_term_id': self.customer_id.property_payment_term_id.id or self.env['account.move'].default_get(['invoice_payment_term_id']).get('invoice_payment_term_id'),
                'default_invoice_origin': self.ref_num,
                'default_user_id': self.user_id.id,
            })
        action['context'] = context
        return action

    @api.model         
    def shipment_calc(self):
        print("yeeeeeeh")
        for freigh in self:
            route_shipments = freigh.freights_routes_shipment
            if len(freigh.freights_route) > 0:
                point=freigh.freights_route[0].point.name
                helper_arr=[]
                i = 0
                for rec in freigh.freights_route:
                    for shipment in freigh.freights_shipment:
                        helper_arr.append({
                            'id' : rec._origin.id,
                            'shipment_id' : shipment._origin.id
                        })
                # ADD NEW freights.route.shipment
                print("helper_arr", helper_arr)
                for rec in helper_arr:
                    add_in = True
                    for rs in route_shipments:
                        if rs.route_point_new.id == rec['id'] and rs.shipment_id.id == rec['shipment_id']:
                            add_in = False
                    for rs in freigh.freights_routes_shipment:
                        if not rs.route_point_new:
                            freigh.freights_routes_shipment -= rs
                    print(rec['id'], rec['shipment_id'], add_in)
                    if add_in:
                        route_shipment=self.env['freights.route.shipment'].create({
                            'route_point_new' : rec['id'],
                            'shipment_id' : rec['shipment_id']
                        })
                    
                        freigh.freights_routes_shipment += route_shipment
                    # else:
                    #     route_shipment=self.env['freights.route.shipment'].search(['&', ('route_point','=', rec['route_point']), ('shipment_id', '=', rec['shipment_id'])],limit=1)             
                    #     if route_shipment:
                    #         route_shipment.write({'sequence' : rec['sequence']})
                # REMOVE NEW freights.route.shipment
                # for rs in route_shipments:
                #     remove_rs = True
                #     for rec in helper_arr:
                #         if rs.route_point.id == rec['route_point'] and rs.shipment_id.id == rec['shipment_id']:
                #             remove_rs = False
                #     if remove_rs:
                #         freigh.freights_routes_shipment -= rs
                #         rs.unlink()

    @api.model
    def get_dashboard_data(self):
        # ('created', 'Created'),
        #     ('quotation', 'Quotation'),
        #     ('re-inquiry', 'Re-inquiry'),
        #     ('confirmed', 'Confirmed'),
        #     ('on-going', 'On going'),
        #     ('arrived', 'Arrived'),
        #     ('released', 'Released'),
        #     ('closed', 'Closed'),
        #     ('cancelled', 'Cancelled'),

        self.env.cr.execute('''SELECT state_id, COUNT(*) as count FROM mlworldwide_freights GROUP BY state_id''', )
        freights = self.env.cr.dictfetchall()

        self.env.cr.execute('''SELECT state_id, COUNT(*) as count FROM freights_quotations GROUP BY state_id''', )
        quotations = self.env.cr.dictfetchall()

        #*************************   Departure
        self.env.cr.execute('''SELECT COUNT(tracks.*) FROM mlworldwide_freights LEFT JOIN freights_route_shipment tracks ON mlworldwide_freights.id=tracks.freights_id AND tracks.etd_date IS NOT NULL AND tracks.atd_date IS NULL LEFT JOIN freights_points points ON tracks.route_point=points.id''', )
        departure_total_ect = self.env.cr.dictfetchall()

        self.env.cr.execute('''SELECT COUNT(tracks.*) FROM mlworldwide_freights LEFT JOIN freights_route_shipment tracks ON mlworldwide_freights.id=tracks.freights_id AND tracks.etd_date IS NOT NULL AND tracks.atd_date IS NOT NULL LEFT JOIN freights_points points ON tracks.route_point=points.id''', )
        departure_total_act = self.env.cr.dictfetchall()

        self.env.cr.execute('''SELECT COUNT(tracks.*) FROM mlworldwide_freights LEFT JOIN freights_route_shipment tracks ON mlworldwide_freights.id=tracks.freights_id AND (DATE_PART('day', date_trunc('day', now()) - date_trunc('day', tracks.etd_date)) + 1)>=0 AND (DATE_PART('day', date_trunc('day', now()) - date_trunc('day', tracks.etd_date)) + 1)<5 AND tracks.atd_date IS NULL AND tracks.ata_date IS NULL AND tracks.eta_date IS NULL LEFT JOIN freights_points points ON tracks.route_point=points.id''', )
        departure_in5_ect = self.env.cr.dictfetchall()

        self.env.cr.execute('''SELECT COUNT(tracks.*) FROM mlworldwide_freights LEFT JOIN freights_route_shipment tracks ON mlworldwide_freights.id=tracks.freights_id AND (DATE_PART('day', date_trunc('day', now()) - date_trunc('day', tracks.atd_date)) + 1)>=0 AND (DATE_PART('day', date_trunc('day', now()) - date_trunc('day', tracks.atd_date)) + 1)<5 AND tracks.ata_date IS NULL AND tracks.eta_date IS NULL LEFT JOIN freights_points points ON tracks.route_point=points.id''', )
        departure_in5_act = self.env.cr.dictfetchall()

        self.env.cr.execute('''SELECT COUNT(tracks.*) FROM mlworldwide_freights LEFT JOIN freights_route_shipment tracks ON mlworldwide_freights.id=tracks.freights_id AND (DATE_PART('day', date_trunc('day', now()) - date_trunc('day', tracks.etd_date)) + 1)>=5 AND tracks.atd_date IS NULL AND tracks.ata_date IS NULL AND tracks.eta_date IS NULL LEFT JOIN freights_points points ON tracks.route_point=points.id''', )
        departure_late_ect = self.env.cr.dictfetchall()

        self.env.cr.execute('''SELECT COUNT(tracks.*) FROM mlworldwide_freights LEFT JOIN freights_route_shipment tracks ON mlworldwide_freights.id=tracks.freights_id AND (DATE_PART('day', date_trunc('day', now()) - date_trunc('day', tracks.atd_date)) + 1)>=5 AND tracks.ata_date IS NULL AND tracks.eta_date IS NULL LEFT JOIN freights_points points ON tracks.route_point=points.id''', )
        departure_late_act = self.env.cr.dictfetchall()
        
        #*************************   Border Arrival
        self.env.cr.execute('''SELECT COUNT(tracks.*) FROM mlworldwide_freights LEFT JOIN freights_route_shipment tracks ON mlworldwide_freights.id=tracks.freights_id AND tracks.eta_date IS NOT NULL LEFT JOIN freights_points points ON tracks.route_point=points.id AND points.border=true''', )
        ba_total_ect = self.env.cr.dictfetchall()

        self.env.cr.execute('''SELECT COUNT(tracks.*) FROM mlworldwide_freights LEFT JOIN freights_route_shipment tracks ON mlworldwide_freights.id=tracks.freights_id AND tracks.ata_date IS NOT NULL LEFT JOIN freights_points points ON tracks.route_point=points.id AND points.border=true''', )
        ba_total_act = self.env.cr.dictfetchall()

        self.env.cr.execute('''SELECT COUNT(tracks.*) FROM mlworldwide_freights LEFT JOIN freights_route_shipment tracks ON mlworldwide_freights.id=tracks.freights_id AND (DATE_PART('day', date_trunc('day', now()) - date_trunc('day', tracks.eta_date)) + 1)>=0 AND (DATE_PART('day', date_trunc('day', now()) - date_trunc('day', tracks.eta_date)) + 1)<5 AND tracks.ata_date IS NULL LEFT JOIN freights_points points ON tracks.route_point=points.id AND points.border=true''', )
        ba_in5_ect = self.env.cr.dictfetchall()

        self.env.cr.execute('''SELECT COUNT(tracks.*) FROM mlworldwide_freights LEFT JOIN freights_route_shipment tracks ON mlworldwide_freights.id=tracks.freights_id AND (DATE_PART('day', date_trunc('day', now()) - date_trunc('day', tracks.ata_date)) + 1)>=0 AND (DATE_PART('day', date_trunc('day', now()) - date_trunc('day', tracks.ata_date)) + 1)<5 LEFT JOIN freights_points points ON tracks.route_point=points.id AND points.border=true''', )
        ba_in5_act = self.env.cr.dictfetchall()

        self.env.cr.execute('''SELECT COUNT(tracks.*) FROM mlworldwide_freights LEFT JOIN freights_route_shipment tracks ON mlworldwide_freights.id=tracks.freights_id AND (DATE_PART('day', date_trunc('day', now()) - date_trunc('day', tracks.eta_date)) + 1)>=5 AND tracks.ata_date IS NULL LEFT JOIN freights_points points ON tracks.route_point=points.id AND points.border=true''', )
        ba_late_ect = self.env.cr.dictfetchall()

        self.env.cr.execute('''SELECT COUNT(tracks.*) FROM mlworldwide_freights LEFT JOIN freights_route_shipment tracks ON mlworldwide_freights.id=tracks.freights_id AND (DATE_PART('day', date_trunc('day', now()) - date_trunc('day', tracks.ata_date)) + 1)>=5 LEFT JOIN freights_points points ON tracks.route_point=points.id AND points.border=true''', )
        ba_late_act = self.env.cr.dictfetchall()

        #*************************   Border Departure
        self.env.cr.execute('''SELECT COUNT(tracks.*) FROM mlworldwide_freights LEFT JOIN freights_route_shipment tracks ON mlworldwide_freights.id=tracks.freights_id AND tracks.etd_date IS NOT NULL LEFT JOIN freights_points points ON tracks.route_point=points.id AND points.border=true''', )
        bd_total_ect = self.env.cr.dictfetchall()

        self.env.cr.execute('''SELECT COUNT(tracks.*) FROM mlworldwide_freights LEFT JOIN freights_route_shipment tracks ON mlworldwide_freights.id=tracks.freights_id AND tracks.atd_date IS NOT NULL LEFT JOIN freights_points points ON tracks.route_point=points.id AND points.border=true''', )
        bd_total_act = self.env.cr.dictfetchall()

        self.env.cr.execute('''SELECT COUNT(tracks.*) FROM mlworldwide_freights LEFT JOIN freights_route_shipment tracks ON mlworldwide_freights.id=tracks.freights_id AND (DATE_PART('day', date_trunc('day', now()) - date_trunc('day', tracks.etd_date)) + 1)>=0 AND (DATE_PART('day', date_trunc('day', now()) - date_trunc('day', tracks.etd_date)) + 1)<5 LEFT JOIN freights_points points ON tracks.route_point=points.id AND points.border=true''', )
        bd_in5_ect = self.env.cr.dictfetchall()

        self.env.cr.execute('''SELECT COUNT(tracks.*) FROM mlworldwide_freights LEFT JOIN freights_route_shipment tracks ON mlworldwide_freights.id=tracks.freights_id AND (DATE_PART('day', date_trunc('day', now()) - date_trunc('day', tracks.atd_date)) + 1)>=0 AND (DATE_PART('day', date_trunc('day', now()) - date_trunc('day', tracks.atd_date)) + 1)<5 LEFT JOIN freights_points points ON tracks.route_point=points.id AND points.border=true''', )
        bd_in5_act = self.env.cr.dictfetchall()

        self.env.cr.execute('''SELECT COUNT(tracks.*) FROM mlworldwide_freights LEFT JOIN freights_route_shipment tracks ON mlworldwide_freights.id=tracks.freights_id AND (DATE_PART('day', date_trunc('day', now()) - date_trunc('day', tracks.etd_date)) + 1)>=5 LEFT JOIN freights_points points ON tracks.route_point=points.id AND points.border=true''', )
        bd_late_ect = self.env.cr.dictfetchall()

        self.env.cr.execute('''SELECT COUNT(tracks.*) FROM mlworldwide_freights LEFT JOIN freights_route_shipment tracks ON mlworldwide_freights.id=tracks.freights_id AND (DATE_PART('day', date_trunc('day', now()) - date_trunc('day', tracks.atd_date)) + 1)>=5 LEFT JOIN freights_points points ON tracks.route_point=points.id AND points.border=true''', )
        bd_late_act = self.env.cr.dictfetchall()

        #*************************   Arrival
        self.env.cr.execute('''SELECT COUNT(tracks.*) FROM mlworldwide_freights LEFT JOIN freights_route_shipment tracks ON mlworldwide_freights.id=tracks.freights_id AND tracks.eta_date IS NOT NULL AND tracks.ata_date IS NULL LEFT JOIN freights_points points ON tracks.route_point=points.id''', )
        arrival_total_ect = self.env.cr.dictfetchall()

        self.env.cr.execute('''SELECT COUNT(tracks.*) FROM mlworldwide_freights LEFT JOIN freights_route_shipment tracks ON mlworldwide_freights.id=tracks.freights_id AND tracks.eta_date IS NOT NULL AND tracks.ata_date IS NOT NULL LEFT JOIN freights_points points ON tracks.route_point=points.id''', )
        arrival_total_act = self.env.cr.dictfetchall()

        self.env.cr.execute('''SELECT COUNT(tracks.*) FROM mlworldwide_freights LEFT JOIN freights_route_shipment tracks ON mlworldwide_freights.id=tracks.freights_id AND (DATE_PART('day', date_trunc('day', now()) - date_trunc('day', tracks.eta_date)) + 1)>=0 AND (DATE_PART('day', date_trunc('day', now()) - date_trunc('day', tracks.eta_date)) + 1)<5 LEFT JOIN freights_points points ON tracks.route_point=points.id''', )
        arrival_in5_ect = self.env.cr.dictfetchall()

        self.env.cr.execute('''SELECT COUNT(tracks.*) FROM mlworldwide_freights LEFT JOIN freights_route_shipment tracks ON mlworldwide_freights.id=tracks.freights_id AND (DATE_PART('day', date_trunc('day', now()) - date_trunc('day', tracks.ata_date)) + 1)>=0 AND (DATE_PART('day', date_trunc('day', now()) - date_trunc('day', tracks.ata_date)) + 1)<5 LEFT JOIN freights_points points ON tracks.route_point=points.id''', )
        arrival_in5_act = self.env.cr.dictfetchall()

        self.env.cr.execute('''SELECT COUNT(tracks.*) FROM mlworldwide_freights LEFT JOIN freights_route_shipment tracks ON mlworldwide_freights.id=tracks.freights_id AND (DATE_PART('day', date_trunc('day', now()) - date_trunc('day', tracks.eta_date)) + 1)>=5 LEFT JOIN freights_points points ON tracks.route_point=points.id''', )
        arrival_late_ect = self.env.cr.dictfetchall()

        self.env.cr.execute('''SELECT COUNT(tracks.*) FROM mlworldwide_freights LEFT JOIN freights_route_shipment tracks ON mlworldwide_freights.id=tracks.freights_id AND (DATE_PART('day', date_trunc('day', now()) - date_trunc('day', tracks.ata_date)) + 1)>=5 LEFT JOIN freights_points points ON tracks.route_point=points.id''', )
        arrival_late_act = self.env.cr.dictfetchall()

        return {
            'freights': freights, 
            'quotations': quotations,
            'departure_total_ect': departure_total_ect,
            'departure_in5_ect': departure_in5_ect,
            'departure_late_ect': departure_late_ect,
            'departure_ontime_ect': departure_total_ect[0]['count'] - departure_late_ect[0]['count'] - departure_in5_ect[0]['count'],
            'departure_total_act': departure_total_act,
            'departure_in5_act': departure_in5_act,
            'departure_late_act': departure_late_act,
            'departure_ontime_act': departure_total_act[0]['count'] - departure_late_act[0]['count'] - departure_in5_act[0]['count'],
            
            'ba_total_ect': ba_total_ect,
            'ba_in5_ect': ba_in5_ect,
            'ba_late_ect': ba_late_ect,
            'ba_ontime_ect': ba_total_ect[0]['count'] - ba_late_ect[0]['count'] - ba_in5_ect[0]['count'],
            'ba_total_act': ba_total_act,
            'ba_in5_act': ba_in5_act,
            'ba_late_act': ba_late_act,
            'ba_ontime_act': ba_total_act[0]['count'] - ba_late_act[0]['count'] - ba_in5_act[0]['count'],

            'bd_total_ect': bd_total_ect,
            'bd_in5_ect': bd_in5_ect,
            'bd_late_ect': bd_late_ect,
            'bd_ontime_ect': bd_total_ect[0]['count'] - bd_late_ect[0]['count'] - bd_in5_ect[0]['count'],
            'bd_total_act': bd_total_act,
            'bd_in5_act': bd_in5_act,
            'bd_late_act': bd_late_act,
            'bd_ontime_act': bd_total_act[0]['count'] - bd_late_act[0]['count'] - bd_in5_act[0]['count'],

            'arrival_total_ect': arrival_total_ect,
            'arrival_in5_ect': arrival_in5_ect,
            'arrival_late_ect': arrival_late_ect,
            'arrival_ontime_ect': arrival_total_ect[0]['count'] - arrival_late_ect[0]['count'] - arrival_in5_ect[0]['count'],
            'arrival_total_act': arrival_total_act,
            'arrival_in5_act': arrival_in5_act,
            'arrival_late_act': arrival_late_act,
            'arrival_ontime_act': arrival_total_act[0]['count'] - arrival_late_act[0]['count'] - arrival_in5_act[0]['count'],
        }
    
    def create_order_invoice(self):
        print("create_order_invoice")

        return {
            'name': 'Freight invoice',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'freights.invoice.create',
            'view_id': self.env.ref('ml_worldwide-main.freights_invoice_create_wizard_form').id,
            'target':"new",
            'context': {"default_freight_id": self.id},
        }

        print(self)
        order_lines = []
        for rec in self.freights_payments:
            # if rec.state != 'Cancelled':
            #     raise UserError(_("Please change new state "))
            print(rec)
            print(rec.type)
            product_id = self.env["product.product"].search([('name','=',rec.type)], limit=1)
            if product_id:
                if not (rec.service_desc == "" or rec.service_qty == 0 or rec.service_rate == 0 ):
                    order_lines.append(
                        (
                            0, 0, 
                            {
                                'name': rec.service_desc, 
                                # 'product_id': product_id.id, 
                                'product_uom_qty': rec.service_qty, 
                                'price_unit': rec.service_rate 
                            }
                        ),
                    )
        
        print(order_lines)
        line_name = ""
        last_name = ""
        
        for route in self:
            if line_name == "":
                line_name += str(route.origin_point_id.name)
            last_name = (route.destination_point_id.name)    
        line_name = line_name + " - " + last_name
                               
        if len(order_lines) == 0:
             raise UserError(_("Please check service line"))
         
        sale_order = self.env['sale.order'].sudo().create({
            'name': self.ref_num,
            'partner_id':self.customer_id.id,
            'inv_line_name': line_name, 
            'order_line':order_lines
        })
        sale_order.action_confirm()
        # self.is_sale_order_button = True
        self.order_id=sale_order.id
        
        payment = self.env['sale.advance.payment.inv'].with_context({
            'active_model': 'sale.order',
            'active_ids': [sale_order.id ],
            'active_id': sale_order.id,
            'default_journal_id': self.company_id['account_opening_journal_id'].id,
        }).create({
            'advance_payment_method': 'delivered'
        })
        payment.create_invoices()
        print("------------------",sale_order)
        print("------------------",sale_order.invoice_ids)
        invoice = sale_order.invoice_ids[0]
        invoice.freights_id = self._origin.id
        # invoice.company_id = self.company_id
        # invoice.consignee_id= self.consignee_id

        # report = self.env['ir.actions.report']._get_report_from_name('account.report_invoice_with_payments')
        print("CREATED INVOICE")
        print(invoice)
        print(invoice.get_portal_url())
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': invoice.get_portal_url(),
        }
    def custom_date_ata(self):
        print("************************************************************")
        return {
            'name': 'Freight shippemts',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'freights.route.shipment.wizard',
            'view_id': self.env.ref('ml_worldwide-main.freights_route_shipment_wizard_form').id,
            'target':"new",
            'context': {"default_freight_id": self.id, "default_type_date": "ATA"},
        }
    def custom_date_eta(self):
        print("************************************************************")
        return {
            'name': 'Freight shippemts',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'freights.route.shipment.wizard',
            'view_id': self.env.ref('ml_worldwide-main.freights_route_shipment_wizard_form').id,
            'target':"new",
            'context': {"default_freight_id": self.id, "default_type_date": "ETA"},
        }
    def custom_date_atd(self):
        print("************************************************************")
        return {
            'name': 'Freight shippemts',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'freights.route.shipment.wizard',
            'view_id': self.env.ref('ml_worldwide-main.freights_route_shipment_wizard_form').id,
            'target':"new",
            'context': {"default_freight_id": self.id, "default_type_date": "ATD"},
        }
    def custom_date_etd(self):
        print("************************************************************")
        return {
            'name': 'Freight shippemts',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'freights.route.shipment.wizard',
            'view_id': self.env.ref('ml_worldwide-main.freights_route_shipment_wizard_form').id,
            'target':"new",
            'context': {"default_freight_id": self.id, "default_type_date": "ETD"},
        }
    