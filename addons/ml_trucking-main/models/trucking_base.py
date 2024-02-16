# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-10-24

from email.policy import default
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime
from datetime import timedelta
from datetime import datetime, timedelta

class TruckingBaseModel(models.Model):
    _name = "mltrucking.base"
    _inherit = ['mail.thread']
    _description = "ML Trucking base model"
    _rec_name = 'ref'

    def _get_default_state(self):
        state = self.env.ref('trucking_state_new_request', raise_if_not_found=False)
        return state if state and state.id else False
    
    def _get_user(self):
        print("get_agent")  
        return self.env.user

    core_id = fields.Many2one(comodel_name="mltrucking.core")
    swap_id = fields.Many2one(comodel_name="mltrucking.base")
    ref = fields.Char(string='Reference', default=lambda self: self.env["mltrucking.base"].compute_name(),) # copy=False, tracking=True, compute='_compute_name', readonly=True, store=True) #default=lambda self: self.env['ir.sequence'].next_by_code('mltrucking.base')
    your_date_field = fields.Date(string='Your string', default=datetime.today())
    trucking_type = fields.Many2one(comodel_name="mltrucking.type", string="Type", help="Trucking type") #domain=[('is_active', '=', True)]
    vendor_id = fields.Many2one(comodel_name="res.partner", string="Customer", help="Захиалга өгсөн байгууллага, хувь хүн")
    # vendor_id = fields.Many2one(comodel_name="res.partner", string="Consignee", help="Хүлээн авагч байгууллага, хувь хүн")
    date_begin = fields.Datetime(string="Begin time", help="Ачаа ачих огноо", required=True,)
    date_end = fields.Datetime(string="End time",  help="Ачаа Хүргэх огноо", required=True,)
    total_cost = fields.Float(string='Cost', help="Төсөвлөсөн зардал", compute='compute_total_cost', readonly=True)
    total_rate = fields.Float(string='Rate', help="MLTr баталсан үнэ /НӨАТ-гүй үнэ/", compute='compute_total_rate', readonly=True)
    trucking_terms = fields.Many2one('mltrucking.incoterms', 'Origin term', ) #required=True, track_visibility='onchange'
    user_id = fields.Many2one(comodel_name="res.users", string="User", default=_get_user, help="Захиалга өгсөн менежерийн нэр", required=True)
    currency_id = fields.Many2one(comodel_name='mltrucking.currency', string="Currency", required=True, default=lambda self: self.env['mltrucking.currency'].search([("currency_name","=","MNT")], limit=1), store=True)
    date_diff=fields.Integer(string="TOTAL DAYS", required=True, compute ="calculate_date")
    order_id = fields.Many2one('sale.order', string="Sale order", ondelete="cascade", readonly=True, )
    is_sale_order_button=fields.Boolean(string='Invisibles')
    service_converter=fields.Boolean(default=False)
    cargo_details = fields.Char(string='Cargo details')
    expr_date=fields.Date(string="Exprition Date(Invoice)")
    invoi_date=fields.Date(string="Invoice Date")

    #mail_message_id = fields.Many2one('mail.message', 'Message', required=True, ondelete='cascade', index=True, auto_join=True)
    
    state = fields.Selection([
        ('q_draft', 'Draft'),
        ('q_confirm', 'Confirm'),
        ('q_cancel', 'Cancel'),
        ('q_done', 'Done')
        ], string='Quotation state', default="q_draft", tracking=True)
    
    state_order = fields.Selection([
        ('o_new', 'Confirmed'),
        ('o_ongoing', 'Ongoing'),
        ('o_delivered', 'Delivered'),
        ('o_cancel', 'Cancel'),
        ('o_closed', 'Closed'),
        ], string='Order state', tracking=True)
    
    remark=fields.Char(string='Remark')

    count=fields.Integer()

        
    # freights = fields.Many2many(comodel_name="mltrucking.freight", string="Freight", help="Ачаа нэр")
    truck_services = fields.Many2many(comodel_name="mltrucking.service", string="Services", help="Service нэр", tracking=True)
    truck_inc_notinc = fields.Many2many(comodel_name="mltrucking.include.exclude", string="Include & Not include", help="Service нэр")
    
    #manual_currency = fields.Boolean(string="Manual currency", default = False)
    #currency_rate = fields.Float(string='Currency rate', default = 0.0)

    truck_routes = fields.Many2many(comodel_name="mltrucking.route", string="Route", help="Route нэр", tracking=True)

    truck_order=fields.Many2many(comodel_name='mltrucking.order', string="Order")
    truck_package=fields.Many2many(comodel_name='mltrucking.package', string="Package")

    truck_shipment=fields.Many2many(comodel_name='mltrucking.shipment',string="Shipment")
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)

    truck_photo=fields.Many2many(comodel_name='mltrucking.freight.photo', string="Photos")

    truck_location=fields.Many2many(comodel_name='mltrucking.location', string="Location")

    truck_budget = fields.Many2many(comodel_name="mltrucking.budget", string="Budgets", help="Service нэр", tracking=True)
    
    # inv_data=fields.Char('sale.order' , string="Invoice Name")
    active_docs=fields.Many2one(comodel_name='mltrucking.package')
    # date_diff = fields.Many2many(comodel_name='mltrucking.quotation.data', string="Quotation") 
    # general_id=fields.Many2one(comodel_name='mltrucking.quotation.data',compute="get_general_data" ) # defualt= "get_general_data" 
    def convert_into_budget(self):
        self.service_converter=True
        for rec in self:
            for order in rec.truck_services:
                rec.truck_budget += self.env['mltrucking.budget'].create({
                    'agent_id': order.agent_id.id,
                    'service_desc' : order.service_desc,
                    'service_id' : order.service_id.id,
                    'service_qty' : order.service_qty,
                    'service_cost' : order.service_cost,
                    'total' : order.subtotal_cost
                })
        total=0
        for rec in self.truck_budget:
            total+=rec.service_cost * rec.service_qty
        self.budget_total_cost=total


    def compute_name(self):
        last = self.env['mltrucking.base'].search([('create_date', 'ilike' , fields.Datetime.now().strftime('%Y-%m'))])
        name = "Quoatation/" + str(fields.Datetime.now().year) + '/' + str(fields.Datetime.now().month) + '/' + str(len(last)+1).zfill(5)
        return name

    @api.model
    def create(self, values):
        last = self.env['mltrucking.base'].search([('create_date', 'ilike' , fields.Datetime.now().strftime('%Y-%m'))])
        name = "Quoatation/" + str(fields.Datetime.now().year) + '/' + str(fields.Datetime.now().month) + '/' + str(len(last)+1).zfill(5)
        if not "ref" in values:
            values["ref"] = name
        result = super(TruckingBaseModel, self).create(values) 
        if not "Order" in result.ref:
            core = self.env['mltrucking.core'].create({
                        'truck_quotation': result.id,
                        'truck_state': "draft",
                    })
            result.core_id = core.id
        return result 
    
    def copy(self, default=None):
        self.ensure_one()
        last = self.env['mltrucking.base'].search([('create_date', 'ilike' , fields.Datetime.now().strftime('%Y-%m'))])
        name = "Order/" + str(fields.Datetime.now().year) + '/' + str(fields.Datetime.now().month) + '/' + str(len(last)+1).zfill(5)
        # default = dict(default or {}, sale_order_id=[])
        # default = dict(default or {}, purchase_bill_ids=[])
        # default = dict(default or {}, track_info=[])
        default = dict(default or {}, ref=name)
        default['ref'] = name
        return super(TruckingBaseModel, self).copy(default)
    
    def compute_total_cost(self):
        for rec in self:
            total = 0
            for service in rec.truck_services:
                total += service.service_cost * service.service_qty * service.cost_currency_id.not_ready_sell

            if rec.currency_id:
                if rec.currency_id.not_ready_sell > 0:
                    rec.total_cost = total / rec.currency_id.not_ready_sell
                else:
                    rec.total_cost = total 
            else:
                rec.total_cost = total 

    def compute_total_rate(self):
        for rec in self:
            total = 0
            for service in rec.truck_services:
                total += service.service_rate * service.service_qty * service.rate_currency_id.not_ready_sell

            if rec.currency_id:
                if rec.currency_id.not_ready_sell > 0:
                    rec.total_rate = total / rec.currency_id.not_ready_sell   
                else:
                    rec.total_rate = total 
            else:
                rec.total_rate = total  
     
    @api.onchange('currency_id')
    def onchange_currency_id(self):
        for rec in self:
            rec.compute_total_cost()
            rec.compute_total_rate()
            rec.currency_id = self.currency_id

    @api.onchange('state')
    def onchange_state(self):
        for rec in self:
            if rec._origin.id:
                core = rec.core_id
                if rec.state == "q_done" and not core.truck_order:
                    truck = rec.copy()
                    truck.state_order = "o_new"
                    main = self.env['mltrucking.base'].browse(rec._origin.id)
                    main.swap_id = truck
                    truck.swap_id = main
                    core.truck_order = truck
                    core.truck_state = str(rec.state) + " - " + str(truck.state_order)
        #     raise UserError(_("Please save new quoatation"))

    def action_confirm(self):
        print("Confirm")    
   
    
    def action_cancel(self):
        print("Cancel")    
    
    def action_view_quotation(self):
        report = self.env['ir.actions.report']._get_report_from_name('mltrucking_quotation')
        report.report_type = 'qweb-html'
        html = report.report_action(self, config = False)
        return html

    def action_get_quotation(self):
        print("action_get_quotation")
        report = self.env['ir.actions.report']._get_report_from_name('mltrucking_quotation')
        report.report_type = 'qweb-pdf'
        pdf = report.report_action(self, config = False)
        print(pdf)
        return pdf    
    # route_helper_arr=[]
    def action_get_document(self):
        # self.route_helper_arr.append([])
        # i=0
        # if len(self.truck_routes) != 0:
        #     helper_route_str=self.truck_routes[0].vehicle.name
        #     for route in self.truck_routes:
        #         if helper_route_str == route.vehicle.name:
        #             self.route_helper_arr[i].append(route)
        #         else:
        #             self.route_helper_arr.append([route])
        #             helper_route_str=route.vehicle.name
        #             i+=1
        print(self.id,'-------------------')
        report = self.env['ir.actions.report']._get_report_from_name('mltrucking_document')
        report.report_type = 'qweb-pdf'
        pdf = report.report_action(self, config = False)
        return pdf  
    estimated_time=fields.Char()
    def print_budget(self):
        self.estimated_time=self.date_end-self.date_begin
        report = self.env['ir.actions.report']._get_report_from_name('mltrucking_budget')
        report.report_type = 'qweb-pdf'
        pdf = report.report_action(self, config = False)
        if len(self.truck_budget)  != 0 :
            return pdf   

    
    def convert_order(self):
        print(self.id,'-----------------------------++++')
        order_lines = []
        for rec in self.truck_services:
            # if rec.state != 'Cancelled':
            #     raise UserError(_("Please change new state "))
                
            if not (rec.service_desc == "" or rec.service_qty == 0 or rec.service_cost == 0 ):
                order_lines.append(
                    (0, 0, {'name': rec.service_desc, 'product_id': rec.service_id.id, 'product_uom_qty': rec.service_qty, 'price_unit': rec.service_cost }),
                )
            
                       
        if len(order_lines) == 0:
             raise UserError(_("Please check service line"))
         
        sale_order = self.env['sale.order'].sudo().create({
            'name': self.ref,
            'partner_id':self.vendor_id.id,
            'order_line':order_lines,
            'base_id' : self.id
        })
        
        return sale_order.action_quotation_send()


    def create_sale_order(self):       
        print(self)
        order_lines = []
        for rec in self.truck_budget:
            # if rec.state != 'Cancelled':
            #     raise UserError(_("Please change new state "))
                
            if not (rec.service_desc == "" or rec.service_qty == 0 or rec.service_sale == 0 ):
                order_lines.append(
                    (0, 0, {'name': rec.service_desc, 'product_id': rec.service_id.id, 'product_uom_qty': rec.service_qty, 'price_unit': rec.service_sale }),
                )
        
        line_name = ""
        last_name = ""
        
        for route in self.truck_routes:
            if line_name == "":
                line_name += str(route.origin.name)
            last_name = (route.destination.name)    
        line_name = line_name + " - " + last_name
                               
        if len(order_lines) == 0:
             raise UserError(_("Please check service line"))
         
        sale_order = self.env['sale.order'].sudo().create({
            'name': self.ref,
            'partner_id':self.vendor_id.id,
            'inv_line_name': line_name, 
            'order_line':order_lines
            
        })
        sale_order.action_confirm()
        self.is_sale_order_button = True
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

        invoice = sale_order.invoice_ids[0]
        invoice.trucking_id = self._origin.id
        # invoice.company_id = self.company_id
        # invoice.vendor_id= self.vendor_id

        # report = self.env['ir.actions.report']._get_report_from_name('account.report_invoice_with_payments')
        print("CREATED INVOICE")
        print(invoice)
        print(invoice.get_portal_url())
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': invoice.get_portal_url(),
            
        }
    
    # @api.onchange('truck_routes')
    # def give_color(self):
    #     arr=[]
    #     helper_arr=[]
    #     for rec in self.truck_routes:
    #         helper_arr.append(rec)
    #         if rec.b != 'b':
    #             rec.b = 'b'
    #         if len(arr)== 0:
    #             arr.append(rec)
    #             rec.a = arr[0].origin.name
    #         else:
    #             rec.a='a'
    #     if len(helper_arr) != 0:
    #         if helper_arr[len(helper_arr)-1]:
    #             rec.b=helper_arr[len(helper_arr)-1].origin.name
        
    bool_shipment_route=fields.Boolean()
    def action_shipment_routes(self):
        arr=[]
        for rec in self.truck_shipment:
            for i in range(len(self.truck_routes)):
                arr.append({
                        'vehicle' : rec.vehicle_rel_id,
                        'ETD': self.truck_routes[i].ETD,
                        'ETA': self.truck_routes[i].ETA,
                        'ATD': self.truck_routes[i].ATD,
                        'ATA': self.truck_routes[i].ATA,
                        'origin': self.truck_routes[i].origin_related,
                        'origin_city' : self.truck_routes[i].origin_city_related,
                        'destination': self.truck_routes[i].destination_related,
                        'dest_city': self.truck_routes[i].dest_city_related,
                    })
        
        # TODO oilgomjgui code baisan tuyl tur commentolloo
        # for rec in self:
        #     for a in rec.truck_routes:
        #         a.unlink()
        # for rec in arr:
        #     self.truck_routes+=self.env['mltrucking.route'].create(rec)
        # self.give_color()
        self.bool_shipment_route=True
    
    @api.model    
    def get_tiles_data(self):
        base = self.env['mltrucking.base'].search([('state','=','confirmed')])
        total=0
        total_between_countries=0
        total_between_cities=0
        total_within_the_city=0
        other_total_between_countries=0
        other_total_between_cities=0
        other_total_within_city=0
        other_total=0
        arr=[]
        other_arr=[]
        for rec in base:
            for shipment in rec.truck_shipment:
                isEmployee=shipment.vehicle.driver_id.is_employee
                if isEmployee == True:
                    vehicle_name=shipment.vehicle_rel
                    for route in rec.truck_routes:
                        if route.vehicle.name == vehicle_name:
                            arr.append(route)
                else:
                    vehicle_name=shipment.vehicle_rel
                    for route in rec.truck_routes:
                        if route.vehicle.name == vehicle_name:
                            other_arr.append(route)
        helper_arr=[]
        i=0
        if len(arr) != 0:
            helper_arr.append([])
            helper_name=arr[0].vehicle.name
            for rec in arr:
                if helper_name == rec.vehicle.name:
                    helper_arr[i].append(rec)
                else:
                    helper_arr.append([rec])
                    helper_name=rec.vehicle.name
                    i+=1

            for rec in helper_arr:
                if rec[0].origin.name != rec[len(rec)-1].destination.name:
                    total_between_countries+=1
                elif rec[0].origin.name == rec[len(rec)-1].destination.name and (rec[0].origin_city.name != rec[len(rec)-1].dest_city.name or (rec[0].origin_city.name == False and rec[len(rec)-1].dest_city.name == False)):
                    total_between_cities+=1
                elif rec[0].origin_city.name == rec[len(rec)-1].dest_city.name and rec[0].origin_city.name != False:
                    total_within_the_city+=1
        total=len(helper_arr)
        other_helper_name=0
        other_helper_arr=[]
        other_i=0
        if len(other_arr) != 0:
            other_helper_arr.append([])
            other_helper_name=other_arr[0].vehicle.name
            for rec in other_arr:
                if other_helper_name == rec.vehicle.name:
                    print('.........,,,')
                    other_helper_arr[other_i].append(rec)
                else:
                    other_helper_arr.append([rec])
                    other_helper_name=rec.vehicle.name
                    other_i+=1
            for rec in other_helper_arr:
                if rec[0].origin.name != rec[len(rec)-1].destination.name:
                    other_total_between_countries+=1
                elif rec[0].origin.name == rec[len(rec)-1].destination.name and (rec[0].origin_city.name != rec[len(rec)-1].dest_city.name or (rec[0].origin_city.name == False and rec[len(rec)-1].dest_city.name == False)):
                    other_total_between_cities+=1
                elif rec[0].origin_city.name == rec[len(rec)-1].dest_city.name and rec[0].origin_city.name != False:
                    other_total_within_city+=1
        other_total=len(other_helper_arr)
        planned_cost_arr=[]
        # total_rate_arr=[]
        budget_arr=[]
        days_of_data=30
        prev_month=5
        graph_months=[]
        today = datetime.today()
        while prev_month > 0:
            today = (today + timedelta(days=-days_of_data))
            year_month=today.strftime('%Y-%m')
            prev_months=year_month.split('-')[1]
            graph_months.append(prev_months)
            previous_months_datas=self.env['mltrucking.base'].search([('create_date','ilike', year_month+'%')])
            planned_cost = 0
            budget = 0
            for rec in previous_months_datas:
                if len(rec.truck_budget) !=0 :
                    if rec.currency_id.currency_name != self.env.company.currency_id.name:
                        planned_cost += rec.total_cost / rec.currency_id.not_ready_sell
                        budget += rec.truck_budget[0].total / rec.currency_id.not_ready_sell
                    else: 
                        planned_cost += rec.total_cost
                        budget += rec.truck_budget[0].total
            planned_cost_arr.append(planned_cost)
            budget_arr.append(budget)
            # total_rate_arr.append(total_rate)
            prev_month-=1
        return {
            'planned_cost': planned_cost_arr,
            'budget': budget_arr,
            'graph_months' : graph_months,
            'total_confirmed_transportation': total,
            'between_countries' : total_between_countries,
            'between_cities' : total_between_cities,
            'within_the_city' : total_within_the_city,
            'other_total_between_countries' : other_total_between_countries,
            'other_total_between_cities' : other_total_between_cities,
            'other_total_within_city' : other_total_within_city,
            'other_total' : other_total
        }    

    # TODO-check email sent 
    def action_send_email(self):
        self.ensure_one()
        template_id = self.env.ref('email_template_name').id
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)

        print(self)
        print(self.ids)

        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'mltrucking.base',
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            # 'mark_agent_mail_sent': False,
            # 'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
            # 'model_description': self.with_context(lang=lang).ref,
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

    def action_send_transport_email(self):
        self.ensure_one()
        template_id = self.env.ref('email_template_transport_name').id
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)

        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'mltrucking.base',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            # 'mark_agent_mail_sent': False,
            # 'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
            # 'model_description': self.with_context(lang=lang).ref,
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
    def create_wizard(self):
        print(self.id,'+++++++++++++++++++++')
        wizard = self.env['test.model'].create({
            'parent_id' : self.id
        })

        return {
            'name': _('Test Wizard'),
            'type': 'ir.actions.act_window',
            'res_model': 'test.model',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new'
        }
    budget_total_cost=fields.Integer()
    
    @api.onchange('truck_budget','truck_services')
    def total_cost_compute(self):
        self.compute_total_cost()
        self.compute_total_rate()

    def generate_order(self):
        for rec in self:
            for order in rec.truck_order:
                rec.truck_package += self.env['mltrucking.package'].create({
                    'description': order.description,
                })

    # @api.onchange('date_begin', 'date_end','date_diff')
    def calculate_date(self):
        if self.date_begin and self.date_end:
            d1=datetime.strptime(str(self.date_begin),'%Y-%m-%d %H:%M:%S') 
            d2=datetime.strptime(str(self.date_end),'%Y-%m-%d %H:%M:%S')
            d3=d2-d1
            self.date_diff=str(d3.days)

    def _get_color(self):
        """Compute Color value according to the conditions"""
        for rec in self:
            if rec.state == "confirmed":
                rec.color = 1
            elif rec.state == 'new_request':
                rec.color = 4
            else:
                rec.color=2
    route_helper_arr=[]
    def helper(self):
        self.route_helper_arr.append([])
        i=0
        if len(self.truck_routes) != 0:
            helper_route_str=self.truck_routes[0].vehicle.name
            for route in self.truck_routes:
                if helper_route_str == route.vehicle.name:
                    self.route_helper_arr[i].append(route)
                else:
                    self.route_helper_arr.append([route])
                    helper_route_str=route.vehicle.name
                    i+=1
        return self.route_helper_arr    
    # helper_arr=fields.Many2one(default=helper)


class MlInheritMail(models.TransientModel):
    _inherit = 'mail.compose.message'
    def _action_send_mail(self, auto_commit=False):
        update_Count=self.env["mltrucking.mail.counter"].search([("mail_id","=",self.res_id)], limit=1)
        if update_Count:
            update_Count.write({
                'count': update_Count.count+1
            })
        else:
            self.env["mltrucking.mail.counter"].create({
                'mail_id': self.res_id,
                'count' : 1,
            })
        change_ui_counter=self.env['mltrucking.base'].search([('id','=', self.res_id)],limit=1)
        change_ui_counter.write({
                'count' : update_Count.count
        })
        return super(MlInheritMail,self)._action_send_mail(auto_commit=auto_commit)


 