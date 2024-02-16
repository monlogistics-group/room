from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta


class FreightPackages(models.Model):
    _name = 'freights.packages'
    _inherit = ['mail.thread', 'mail.activity.mixin','portal.mixin']

    _description = 'Packages'
    # todo : ologosong (date) hiine

    name = fields.Char(string='Cargo name')
    consignee_phone = fields.Char(string='Phone number')
    referral = fields.Char(string="referral", help='invoice, purchage order, freight order, commercial, invoice ...')
    did_check = fields.Char(string='Check')
    delivered = fields.Char(string='Delivered')
    granted = fields.Char(string='Granted')
    attachement_ids = fields.Many2many(comodel_name='ir.attachment', string='File', track_visibility='onchange')
    release_note_remark = fields.Char(string='Release note remark')
    who_updated_customs_date_start = fields.Char()
    who_updated_customs_date_end= fields.Char()
    who_updated_assessment_date_start= fields.Char()
    who_updated_assessment_date_end= fields.Char()
    who_updated_released_date= fields.Char()

    freights_payments = fields.Many2many("freights.payment.service")   
    consignee_id = fields.Many2one(comodel_name='res.partner', string="Consignee")
    
    number_id=fields.Many2one('freights.shipments', string='Shipment ID')
    ppcoll_currency_id = fields.Many2one(comodel_name='res.currency', string="Currency", domain=[ ('active', '=', True)], default=lambda self: self.env.company.currency_id)
    
    package_qty = fields.Integer(string='Package Qty')
    user_id = fields.Integer()

    volume = fields.Float(string='Volume(cbm)')
    gross = fields.Float(string='Gross(kg)')
    ppcoll_price = fields.Float(string='PPColl price')
    shipment=fields.Boolean()

    state_id = fields.Selection(selection=[
        ('confirmed', 'Confirmed'),
        ('on-going', 'Ongoing'),
        ('arrived', 'Arrived'),
        ('border-custom-started', 'Border Custom-Started'),
        ('custom-started', 'Custom-Started'),
        ('custom-ended', 'Custom-Ended'),
        ('releasable', 'Releasable'),
        ('released', 'Released'),
    ],default='confirmed')
    state = fields.Selection(selection=[
        ('late', 'Late')
    ])


    # payments = fields.One2many("freights.payment.service", "package_id")

    customs_boolean = fields.Boolean() 
    terminal_boolean = fields.Boolean() 
    delivery_boolean = fields.Boolean()           

    customs_date_start = fields.Datetime(string='Customs date start')
    customs_date_end = fields.Datetime(string='Customs date end')
    assessment_date_start = fields.Datetime(string='Assesment date start')
    assessment_date_end = fields.Datetime(string='Assesment date end')

    released_date = fields.Date(string='Released Date')
    spent_time = fields.Integer()
    customs_spent_time = fields.Integer()
    customs_date_start_boolean = fields.Boolean()
    customs_date_end_boolean = fields.Boolean()
    assessment_date_start_boolean = fields.Boolean()
    assessment_date_end_boolean = fields.Boolean()
    released_date_boolean = fields.Boolean()
    released_date_button = fields.Boolean()

    customs_date_start_button = fields.Boolean()
    customs_date_end_button = fields.Boolean()
    assessment_date_start_button = fields.Boolean()
    assessment_date_end_button = fields.Boolean()

    date_saver = fields.Char()
    is_late  = fields.Boolean()
    note = fields.Char()
    assessment_late = fields.Char()

    freight_id = fields.Char(compute="_compute_freight_id")
    freight_type = fields.Char()
    employee = fields.Char()
    shipper = fields.Char()
    freight_condition = fields.Char()
    cargo_name = fields.Char()
    terminal = fields.Char()

    customs_filter = fields.Boolean()

    delivery_fiilter = fields.Boolean()

    def qwerty(self):
        return self.env['freights.packages'].search([])
        
    @api.model    
    def get_filtered_records(self):
        packages = self.env['freights.packages'].search([])
        arr = []
        for package in packages:
            if package.terminal not in arr:
                arr.append(package.terminal)
        return arr

    def action_gaali(self):
        self.customs_boolean = True
        self.terminal_boolean = False
        self.delivery_boolean = False
        # self.create_payment()

        wizard = self.env['add.record.to.payments'].create({
            'package_id' : self.id,
            'freights_id' : self.number_id.freights_id.id,
            'shippment_ids' : self.number_id.freights_id.freights_shipment,
            'type': 5,
            'service_desc': 'Customs cost',
            'package': True
        })
        return {
            'name': ('Add Records'),
            'type': 'ir.actions.act_window',
            'res_model': 'add.record.to.payments',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new'
                }
        
    def action_terminal(self):
        wizard = self.env['add.record.to.payments'].create({
            'package_id' : self.id,
            'freights_id' : self.number_id.freights_id.id,
            'package': True,
            'shippment_ids' : self.number_id.freights_id.freights_shipment,
            'type': 2,
            'service_desc': 'Terminal cost',
        })
        return {
            'name': ('Add Records'),
            'type': 'ir.actions.act_window',
            'res_model': 'add.record.to.payments',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new'
        }
        self.customs_boolean = False
        self.terminal_boolean = True
        self.delivery_boolean = False

    def action_delivery(self):
        wizard = self.env['add.record.to.payments'].create({
            'package_id' : self.id,
            'shippment_ids' : self.number_id.freights_id.freights_shipment,
            'freights_id' : self.number_id.freights_id.id,
            'package': True,
            'type': 6,
            'service_desc': 'Delivery cost',
        })
        return {
            'name': ('Add Records'),
            'type': 'ir.actions.act_window',
            'res_model': 'add.record.to.payments',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new'
        }
        self.customs_boolean = False
        self.terminal_boolean = False
        self.delivery_boolean = True

    # compute zasna
    @api.depends('freight_id')
    def _compute_freight_id(self):
        if len(self.number_id)<= 1:
            self.freight_id = self.number_id.freights_id.ref_num
            self.freight_type = self.number_id.freights_id.ordered_freights_type.type_name
            self.employee = self.number_id.freights_id.employee.name
            self.shipper = self.number_id.freights_id.shipper_info
            self.cargo_name = self.number_id.freights_id.notes
            # self.terminal = self.number_id.terminal_id.name
            if self.number_id.freights_id.is_prepaid == False and self.number_id.freights_id.is_export == False:
                self.freight_condition = 'COLL'
            elif self.number_id.freights_id.is_prepaid == True:
                self.freight_condition = 'PPD'
            elif self.number_id.freights_id.is_export == True:
                self.freight_condition = 'EXP'

            for payment in self.number_id.freights_id.freights_payments:
                for shipment in payment.shippment_ids:
                    if self.number_id.name == shipment.name:
                        for type in payment.type:
                            if type.name == 'Customs':
                                self.customs_filter = True
                            elif type.name == 'Delivery':
                                self.delivery_fiilter = True                            
        else:
            self.freight_id = 1                            
        
    def show_wizard(self):
        wizard = self.env['package.wizard'].create({
            'helper_id' : self.id,
        })
        return {
            'name': ('Filter conditions'),
            'type': 'ir.actions.act_window',
            'res_model': 'package.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new'
        }

    @api.onchange("customs_date_start")
    def _onchange_check_date(self):
        if self.customs_date_start:
            for rec in self:
                rec.date_saver = str(datetime.now().strftime('%Y-%m-%d'))

    # @api.onchange("customs_cost",'delivery_cost','terminal_cost')
    # def _onchange_customs_cost(self):
    #     if self.customs_cost != 0:
    #         for freight in self.number_id.freights_id:
    #             for quotation in freight.freights_quotations:
    #                 if quotation.state_id == 'confirmed':
    #                     if quotation.clear_service == False  and quotation.from_declaration == False and quotation.is_thc == False:
    #                         for rec in freights.freights_payments:
    #                             if self.number_id in rec.shipment_ids:
    #                                 rec.service_cost = self.customs_cost 
    #                                 rec.package_id = self.id
    #                                 rec.service_desc = ''



    #                         print(quotation.clear_service,'=====te')




    #         print(self.number_id.freights_id.freights_quotations.clear_service,'===')


    @api.onchange('customs_date_end')      
    def _onchange_custom_end(self):
        fn = self.env['freights.type.assign'].search([], limit=1)
        if self.customs_date_end and self.customs_date_start:
            d1=datetime.strptime(str(self.customs_date_start.strftime('%Y-%m-%d  %H:%M')),'%Y-%m-%d  %H:%M') 
            date_start_timestamp = datetime.timestamp(d1)
            d2=datetime.strptime(str(self.customs_date_end.strftime('%Y-%m-%d  %H:%M')),'%Y-%m-%d  %H:%M')
            date_end_timestamp = datetime.timestamp(d2)
            workday_start = datetime.strptime('09:00:00', '%H:%M:%S')
            workday_end = datetime.strptime('18:00:00', '%H:%M:%S')
            date_start_hour=datetime.strptime(self.customs_date_start.strftime('%H:%M:%S'), '%H:%M:%S')
            date_end_hour=datetime.strptime(self.customs_date_end.strftime('%H:%M:%S'), '%H:%M:%S')
            
            def recursion(date_end_timestamp, date_start_timestamp, hours=0):
                if date_end_timestamp <= date_start_timestamp:
                    worked_hours = workday_end - date_start_hour + (date_end_hour - workday_start )- timedelta(hours=1)
                    a_hours = worked_hours.total_seconds() / 3600
                    # if a_hours == 8:
                    return (hours - 8 + a_hours) / 8
                else:
                    date_end_timestamp -= 3600 * 24
                    timestamp = datetime.fromtimestamp(date_end_timestamp)
                    holidays = self.env["hr.leave"].search([('date_from', '<=', timestamp),('date_to', '>=', timestamp)])
                    is_holiday = False
                    for days in holidays:
                        stat_name = days.holiday_status_id.name.lower()
                        if "holiday" in stat_name:
                            is_holiday = True
                        else:
                            is_holiday = False
                    if datetime.fromtimestamp(date_end_timestamp).weekday() < 5 and is_holiday == False:
                        return recursion(date_end_timestamp, date_start_timestamp, hours+8)
                    else:
                        return recursion(date_end_timestamp, date_start_timestamp, hours)

            self.customs_spent_time = recursion(date_end_timestamp, date_start_timestamp)

        if self.date_saver:
            if self.number_id.freights_id.ordered_freights_type.type_name == 'FCL' or self.number_id.freights_id.ordered_freights_type.type_name == 'FTL' or self.number_id.freights_id.ordered_freights_type.type_name == 'WGN' or self.number_id.freights_id.ordered_freights_type.type_name == 'AIR':
                dates = fn.get_due_date(fields.Datetime.from_string(self.date_saver).date(), 16)
                d1=datetime.strptime(str(fields.Datetime.from_string(dates['end_date']).date()),'%Y-%m-%d') 
                d2=datetime.strptime(str(datetime.now().strftime('%Y-%m-%d')),'%Y-%m-%d')
                d3=d2-d1
                date_diff=str(d3.days)
                if int(date_diff) > 0:
                    self.state = 'late'
            elif self.number_id.freights_id.ordered_freights_type.type_name == 'LCL' or self.number_id.freights_id.ordered_freights_type.type_name == 'LTL' or self.number_id.freights_id.ordered_freights_type.type_name == 'Multimodal':
                dates = fn.get_due_date(fields.Datetime.from_string(self.date_saver).date(), 32)
                d1=datetime.strptime(str(fields.Datetime.from_string(dates['end_date']).date()),'%Y-%m-%d') 
                d2=datetime.strptime(str(datetime.now().strftime('%Y-%m-%d')),'%Y-%m-%d')
                d3=d2-d1
                date_diff=str(d3.days)
                if int(date_diff) > 0:
                    self.state = 'late'
            # elif self.assessment_date_end 
    
    @api.onchange("assessment_date_start")
    def _onchange_assessment_date_start(self):
        if self.assessment_date_start:
            self.assessment_late = str(datetime.now().strftime('%Y-%m-%d'))

    @api.onchange('released_date')
    def _onchange_released_date(self):
        if self.released_date:
            arr = []
            last = self.number_id.freights_id.freights_routes_shipment[len(self.number_id.freights_id.freights_routes_shipment)-1].route_point.name
            for track in self.number_id.freights_id.freights_routes_shipment:
                if track.route_point.name == last:
                    if track.shipment_id.id == self.number_id.id:
                        arr.append({'ata' : track.ata_date})
            d1=datetime.strptime(str(arr[0]['ata'].strftime('%Y-%m-%d')),'%Y-%m-%d') 
            d2=datetime.strptime(str(self.released_date.strftime('%Y-%m-%d')),'%Y-%m-%d')
            d3=d2-d1
            date_diff=str(d3.days)
            self.spent_time = int(date_diff)

                

    @api.onchange("assessment_date_end")
    def _onchange_assessment_date_end(self):
        fn = self.env['freights.type.assign'].search([], limit=1)
        if self.assessment_late:
            dates = fn.get_due_date(fields.Datetime.from_string(self.assessment_late).date(), 8)
            d1=datetime.strptime(str(fields.Datetime.from_string(dates['end_date']).date()),'%Y-%m-%d') 
            d2=datetime.strptime(str(datetime.now().strftime('%Y-%m-%d')),'%Y-%m-%d')
            d3=d2-d1
            date_diff=str(d3.days)
            if date_diff > 0:
                self.state = 'late'

    # create hiih uyd hen create hiisnign hadgalaad herwee date field-vdig bugluj create hiisen bwal dahij edit-leheergv bolgono
    @api.model
    def create(self,vals):
        vals['user_id'] = self.env.user.id
        if vals['customs_date_start'] != False:
            vals['state_id'] = 'border-custom-started'
            vals["customs_date_start_button"] =True
            vals["who_updated_customs_date_start"] = self.env.user.name
            vals["customs_date_start_boolean"] = True

        if vals['customs_date_end'] != False:
            vals["who_updated_customs_date_end"] = self.env.user.name
            vals["customs_date_end_button"] =True
            vals["customs_date_end_boolean"] = True

        if vals['released_date'] != False:
            vals["who_updated_released_date"] = self.env.user.name
            vals["released_date_button"] =True
            vals["released_date_boolean"] = True


        if vals['assessment_date_start'] != False:
            vals["who_updated_assessment_date_start"] = self.env.user.name
            vals["assessment_date_start_button"] =True
            vals["assessment_date_start_boolean"] = True

        if vals['assessment_date_end'] != False:
            vals['state_id'] = 'custom-started'
            vals["who_updated_assessment_date_end"] = self.env.user.name
            vals["assessment_date_end_button"] =True
            vals["assessment_date_end_boolean"] = True

        return super(FreightPackages, self).create(vals)

    # update hiih vyd date field ig uurchilwul hen uurchilsnig hadgalaad dahij uurchluhuurgv bolgono
    def write(self,vals):
        if 'released_date' in vals:
            if self.who_updated_released_date == False:
                self.who_updated_released_date = self.env.user.name
                self.released_date_button = True
                vals['released_date_boolean'] = True
        if 'customs_date_start' in vals:
            self.state_id = 'border-custom-started'
            if self.who_updated_customs_date_start == False:
                self.who_updated_customs_date_start = self.env.user.name
                self.customs_date_start_button =True
                vals["customs_date_start_boolean"] = True
            elif self.who_updated_customs_date_start == self.env.user.name: 
                self.customs_date_start_button =True
                vals["customs_date_start_boolean"] = True
            else:
                vals['customs_date_start'] = self.customs_date_start

        if 'customs_date_end' in vals:
            if self.who_updated_customs_date_end == False:
                self.who_updated_customs_date_end = self.env.user.name
                self.customs_date_end_button =True
                vals["customs_date_end_boolean"] = True
            elif self.who_updated_customs_date_end == self.env.user.name: 
                self.customs_date_end_button =True
                vals["customs_date_end_boolean"] = True
            else:
                vals['customs_date_end'] = self.customs_date_end
        
        if 'assessment_date_start' in vals:
            if self.who_updated_assessment_date_start == False:
                self.who_updated_assessment_date_start = self.env.user.name
                self.assessment_date_start_button =True
                vals["assessment_date_start_boolean"] = True

            elif self.who_updated_assessment_date_start == self.env.user.name: 
                self.assessment_date_start_button =True
                vals["assessment_date_start_boolean"] = True
            else:
                vals['assessment_date_start'] = self.assessment_date_start

        if 'assessment_date_end' in vals:
            self.state_id = 'custom-started'
            if self.who_updated_assessment_date_end == False:
                self.who_updated_assessment_date_end = self.env.user.name
                self.assessment_date_end_button =True
                vals["assessment_date_end_boolean"] = True
            elif self.who_updated_assessment_date_end == self.env.user.name: 
                self.assessment_date_end_button =True
                vals["assessment_date_end_boolean"] = True
            else:
                vals['assessment_date_end'] = self.assessment_date_end

        return super(FreightPackages, self).write(vals)

    # date_start field-g dahij uurchluh huselt tawina adminas
    def send_request_to_admin_customs_date_start(self):
        self.env['package.request'].create({
            'name' : self.env.user.name,
            'where' : 'Packages',
            'field_name' : 'Customs date start',
            'package_id' : self.id,
            'requested_date' : datetime.today().strftime('%Y-%m-%d')
        })
        self.customs_date_start_button = False

    # date_end field-g dahij uurchluh huselt tawina adminas
    def send_request_to_admin_customs_date_end(self):
        self.env['package.request'].create({
            'name' : self.env.user.name,
            'where' : 'Packages',
            'field_name' : 'Customs date end',
            'package_id' : self.id,
            'requested_date' : datetime.today().strftime('%Y-%m-%d')
        })
        self.customs_date_end_button = False

    # assessment_date_start field-g dahij uurchluh huselt tawina adminas
    def send_request_to_admin_assessment_date_start(self):
        self.env['package.request'].create({
            'name' : self.env.user.name,
            'where' : 'Packages',
            'field_name' : 'Assessment date start',
            'package_id' : self.id,
            'requested_date' : datetime.today().strftime('%Y-%m-%d')
        })
        self.assessment_date_start_button = False

    def send_request_to_admin_date(self):
        self.env['package.request'].create({
            'name' : self.env.user.name,
            'where' : 'Packages',
            'field_name' : 'released date',
            'package_id' : self.id,
            'requested_date' : datetime.today().strftime('%Y-%m-%d')
        })
        self.date_button = False
    # assessment_date_end field-g dahij uurchluh huselt tawina adminas
    def send_request_to_admin_assessment_date_end(self):
        self.env['package.request'].create({
            'name' : self.env.user.name,
            'where' : 'Packages',
            'field_name' : 'Assessment date end',
            'package_id' : self.id,
            'requested_date' : datetime.today().strftime('%Y-%m-%d')
        })
        self.assessment_date_end_button = False

    # operation bolon sales-s uur hvn state uurchluh bolomjgv
    # @api.onchange('state_id')
    # def _onchange_state_id(self):
    #     arr = []
    #     for role in self.number_id.freights_id.employee.user_groups:
    #         arr.append(role.name.lower())
    #     if ('operation' or 'sales') not in arr:
    #         raise ValidationError("You don't have permission to perform this action")

    @api.model
    def create(self, values):
        shipment = self.env['freights.shipments'].search([('id', '=', values['number_id'])],limit=1)
        if shipment.terminal_id:
            values['terminal'] = shipment.terminal_id.name
        return super(FreightPackages, self).create(values)

    def goods_pdf(self):
        wizard = self.env['preview.pdf.wizard'].create({
            'freights_package' : self.id
        })
        return {
            'name': ('Pdf Preview'),
            'type': 'ir.actions.act_window',
            'res_model': 'preview.pdf.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new'
        }
        # self.ensure_one()
        # report = self.env['ir.actions.report']._get_report_from_name('ml_worldwide.cargo_receipt')
        # print(report,'----')
        # report.report_type = 'qweb-html'
        # html = report.report_action(self, config = False)
        # return html

    # todo
    # Releasable bolor released state ig invoice duusgasnii daraa hiine
    # document-uud upload hiine
    # busad ireeduid heregtei Fields
    # gaali ehelsen duussan ognoo (Unelgee hyanalm)
    # talbai ehelsen duussan
    # hurgelt ehelsen duussan
    # ogloson ognoo hen hezee
    # edgeer-iig hiihed endees bodt zardluudiig bugluj oruulahad avtomataar manai cost-d burtgegdej yavana
    # AIR achaa bol master bill, house bill cost burtgene
    # gaaliin meduuleg shiveltiin zardluud
