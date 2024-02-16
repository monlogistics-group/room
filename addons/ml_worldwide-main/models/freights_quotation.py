# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-12-02
import calendar
from random import randint

from datetime import timedelta
from datetime import datetime
from datetime import date
from email.policy import default
from odoo import api, fields, models, _,osv
from odoo.exceptions import UserError, ValidationError
import urllib.request as url_request
from bs4 import BeautifulSoup
import json
import math

class FreightsQuotationsModel(models.Model):
    _name = "freights.quotations"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Worldwide freights quotations model"
    _rec_name = 'quotation_ref_num'

    def get_tdb_crawl_data(self, currency_date=None):
        """
        Ядарсан код засав
        Crawl хийж байгаа учир их удаан ажиллна мөн анхны ирсэн хувилбар их болхи аргаар хийгдсэн учир performance-д нөлөөлөхөөр байсныг засаж оруулав.
        """
        url = "http://www.tdbm.mn/script.php?mod=rate&ln=mn"
        with url_request.urlopen(url) as request:
            soup = BeautifulSoup(request.read(), 'html.parser')
            currency = ["USD", "EUR", "CNY", "RUB", "CHF", "GBP", "AUD"]
            data = {}
            data_buy = {}
            call_date = currency_date if currency_date is not None else date.today()
            for name in currency:
                trcurr = soup.find("img", {"title": name}).parent.parent.findChildren("td",recursive=False) if currency_date is None or currency_date == date.today() else \
                         soup.find("img", {"src": "/bundles/tdbm/css/img/icon/currency/" + name + ".png"}).parent.parent.findAll('div')
                buy = float(trcurr[2].string.replace(',', ''))
                sell = float(trcurr[3].string.replace(',', ''))
                data.setdefault(name, sell)
                data_buy.setdefault(name, buy)
            data.setdefault('MNT',1)
            data_buy.setdefault('MNT', 1)
            return call_date, data, data_buy

    def _get_employee_id(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        return employee_rec.id   

    def _get_origin_point(self):
        freight = self.env["mlworldwide.freights"].browse(self.id)
        return freight.origin_point_id

    def _get_destination_point(self):
        freight = self.env["mlworldwide.freights"].browse(self.id)
        return freight.destination_point_id
    
    def get_default_services(self):
        freight = self.env["mlworldwide.freights"].browse(self.env.context.get('default_freight_id'))
        agent=self.env["res.partner"].search([('name', '=', "MLW")], limit=1)
        currency=self.env["res.currency"].search([('name', '=', "MNT")], limit=1)
        
        service_lines = []
        
        if freight and not freight.is_prepaid and agent and currency:
            service_type = self.env['service.types'].search([('purpose', '=', 'Form Declaration Cost')]) 
            service_line = self.env["freights.service"].sudo().create({
                                        'purpose': 'Form Declaration Cost',
                                        'type': 5,
                                        'purpose_radio':service_type.id,
                                        'service_rate': 0 ,
                                        'service_cost': 0 ,
                                        'currency_id' : currency.id,
                                        "rate_currency_id" :  currency.id,
                                        'agent_id': agent.id 
                                })
            service_type1 = self.env['service.types'].search([('purpose', '=', 'Clearance Service')]) 
            service_line1 = self.env["freights.service"].sudo().create({
                                        'purpose': 'Clearance Service',
                                        'type': 5,
                                        'purpose_radio':service_type1.id,
                                        'service_rate': 0 ,
                                        'service_cost': 0 ,
                                        "rate_currency_id" :  currency.id,
                                        'currency_id' : currency.id,
                                        'agent_id': agent.id 
                                })
            service_lines.append(service_line.id)
            service_lines.append(service_line1.id)
        if freight and not freight.is_prepaid and agent and currency: 
            if freight.destination_term.code.upper() == "DAP" or freight.destination_term.code.upper() == "DDU" or freight.destination_term.code.upper() == "DDP":
                service_type = self.env['service.types'].search([('purpose', '=', 'THC')])
                service_line = self.env["freights.service"].sudo().create({
                                        'purpose': 'THC',
                                        'type': 4,
                                        'purpose_radio':service_type.id,
                                        'service_rate': 0 ,
                                        'service_cost': 0 ,
                                        'currency_id' : currency.id,
                                        'agent_id': agent.id 
                                })
                vehicle = self.env["delivery.vehicle"].search([])
                zone = self.env["delivery.zone"].search([])
                service_lines.append(service_line.id)
                if vehicle and zone:
                    service_line1 = self.env["freights.service"].sudo().create({
                                            'purpose': 'Delivery',
                                            'type': 6,
                                            "delivery_zone" : 1,
                                            "fleet" : 1,
                                            'service_rate': 0 ,
                                            'service_cost': 0 ,
                                            'currency_id' : currency.id,
                                            "rate_currency_id" :  currency.id,
                                            'agent_id': agent.id 
                                    })
                    service_lines.append(service_line1.id)
        return service_lines
    
    def compute_currency_values(self):
        """
        Crawl хийж байгаа учир их удаж байгаа.
        """
        rate_date, sell_value, buy_value = self.get_tdb_crawl_data(date.today())
        available_currencies = self.env['res.currency'].search([('active', '=', True)])
        base_buy = buy_value.get(self.env.company.currency_id.name, None)
        currency_lines = []
        if self.currency_ids:
            for line in self.currency_ids:
                currency_rate = sell_value.get(line.currency_id.name, None)
                currency_rate_buy = buy_value.get(line.currency_id.name, None)
                if currency_rate is not None and currency_rate_buy is not None and base_buy is not None:
                    # rate = 1
                    # if line.currency_id.name != self.base_currency.name:
                    #     rate = base_buy / currency_rate
                    # line.update({'sell': currency_rate,
                    #             'buye': currency_rate_buy,
                    #             'rate': rate})
                    currency_lines.append(line.id)
        else:
            for currency in available_currencies:
                currency_rate = sell_value.get(currency.name, None)
                currency_rate_buy = buy_value.get(currency.name, None)
                if currency_rate is not None and currency_rate_buy is not None and base_buy is not None:
                    rate = 1
                    if currency.name != self.env.company.currency_id.name:
                        rate = base_buy / currency_rate
                    newcurr_line = self.env["currency.line"].sudo().create({'currency_id': currency.id,
                                            'sell': currency_rate,
                                            'buy': currency_rate_buy,
                                            'rate': rate,
                                            'freight_quotation_id': self.id})
                    # newcurr_line = [(0, False, {'currency_id': currency.id,
                    #                         'sell': currency_rate,
                    #                         'buy': currency_rate_buy,
                    #                         'rate': rate,
                    #                         'freight_quotation_id': self.id})]
                    currency_lines.append(newcurr_line.id)
        return currency_lines

           
    def _get_default_freight_type(self):
        freight = self.env["mlworldwide.freights"].browse(self.env.context.get('default_freight_id'))
        res = []
        for ttype in freight.freigths_type:
            res.append(ttype.id)
        return json.dumps([('id', 'in', res)])
    
    def _get_default_domain_taras(self):
        freight = self.env["mlworldwide.freights"].browse(self.env.context.get('default_freight_id'))
        res = []
        for ttype in freight.taras_id:
            res.append(ttype.id)
        return json.dumps([('id', 'in', res)])
   
    def _get_default_domain_fcl_route(self):
        freight = self.env["mlworldwide.freights"].browse(self.env.context.get('default_freight_id'))
        res = []
        for ttype in freight.fclroute_ids:
            res.append(ttype.id)
        return json.dumps([('id', 'in', res)])

    def _get_default_gross(self):
        freight = self.env["mlworldwide.freights"].browse(self.env.context.get('default_freight_id'))
        return freight.gross
    
    def _get_default_cbm(self):
        freight = self.env["mlworldwide.freights"].browse(self.env.context.get('default_freight_id'))
        return freight.volume

    def _get_employee_id(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
    
    def _get_default_valid_until_date(self):
        d = datetime.now()
        print("last days", calendar.monthrange(d.year, d.month)[-1])
        
        return datetime(d.year, d.month, calendar.monthrange(d.year, d.month)[-1])
    
    def _get_check_is_sale(self):
        res = False
        if (self.user_has_groups('ml_worldwide-main.group_mlworldwide_sales') or self.user_has_groups('ml_worldwide-main.group_mlworldwide_manager')) and not self.user_has_groups('ml_worldwide-main.group_mlworldwide_pd_manager') and not self.user_has_groups('ml_worldwide-main.group_mlworldwide_pd'):
            res = True
        return res
    
    def _get_check_is_pd(self):
        res = False
        if (not self.user_has_groups('ml_worldwide-main.group_mlworldwide_sales') and not self.user_has_groups('ml_worldwide-main.group_mlworldwide_manager')) and (self.user_has_groups('ml_worldwide-main.group_mlworldwide_pd_manager') or self.user_has_groups('ml_worldwide-main.group_mlworldwide_pd')):
            res = True
        print(res, "qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq")
        return res

    
    @api.depends('service_ids')
    def _compute_ett_min(self):
        # TODO end service-uudiin ett-gees min avaad hadgalna
        for rec in self:
            count = 0
            for service in rec.service_ids:
                count += service.ett
            self.ett_min = count    
    
    # def _compute_valid_until_date(self):
        # TODO end service-uudiin validuntil-aas min avaad hadgalna
        # for rec in self:
        #     rec.valid_until_date = False
    
    freights_id = fields.Many2one(comodel_name="mlworldwide.freights", string="Freight", ondelete="cascade")
    quotation_ref_num = fields.Char(string='Reference', default=lambda self: self.env["freights.quotations"].compute_name()) 
    quote_name = fields.Char(string='Quotation', compute='_compute_quote_name')
    freights_type_ids = fields.Many2one(comodel_name="freights.type", string="Freight type")
    freights_type_name = fields.Char(related="freights_type_ids.type_name", string="Freight type")
    freight_type_domain = fields.Char( readonly=True,compute='_compute_domain_freight_type',default=_get_default_freight_type)
    taras_ids = fields.Many2one(comodel_name="freights.taras", string="Tara")
    fclroute_ids = fields.Many2one(comodel_name="freights.route.category", string="FCL Route")
    container_type = fields.Many2one(comodel_name="freights.container.type", string="Container type")
    gross = fields.Float(related='freights_id.gross', readonly=True, string="Gross weight (kg)", default=_get_default_gross)
    cbm = fields.Float(related='freights_id.volume', readonly=True, string="Volume (cbm)", default=_get_default_cbm)
    chargabel_weight = fields.Float(string="Chargable weight (kg)",readonly=True, compute='_compute_chargable_weight')
    employee = fields.Many2one('hr.employee', string="Employee", default=_get_employee_id, readonly=True, required=True, help="Захиалга өгсөн менежерийн нэр")
    service_ids = fields.One2many("freights.service",'quotation_id', string="Service ids", help="Service нэр", default=get_default_services)
    quote_cost = fields.Float(string='Cost', help="MLTr Төсөвлөсөн үнэ /НӨАТ-гүй үнэ/")
    ett_min = fields.Integer(string="ETT MIN", help="Expected transportation time minimum", defualt=0, force_save='1',compute='_compute_ett_min')
    ett_max = fields.Integer(string="ETT MAX", help="Expected transportation time maximum", defualt=0)
    valid_until_date = fields.Date(string="Valid Until date", help="", default=_get_default_valid_until_date) 
    note = fields.Text(string="Note")
    last_agent_bill = fields.Text(string="Last agent bill instruction")
    reserved_cost = fields.Float(string='Reserved cost', help="", )
    reserved_cost_remark = fields.Text(string='Reserved cost remark', help="", )
    freights_incude_service = fields.One2many("freight.incexc.service", "quotation_id", string="Include service" ) 
    freights_exclude_service = fields.One2many("freight.incexc.service", "quotation_id",string="Exclude service")
    demmurage_start_point = fields.Many2one('freights.points', string='Demmurage start point')
    demmurage_end_point = fields.Many2one('freights.points', string='Demmurage end point')
    free_days = fields.Integer(string='Free days')
    consignee = fields.Many2one(comodel_name='res.partners')
    shipping_line=fields.Many2one(comodel_name="freights.shipping.line", string="Shipping line", help="Container type")
    container_owner = fields.Many2one(comodel_name="res.partner", string="Container owner", help="" , domain="[('is_company','=', True)]")
    agent_id = fields.Many2one(comodel_name="res.partner", string="Agent")
    #may be needed
    abroad_rate = fields.Float(string='Abroad rate', help="", )
    abroad_rate_currency = fields.Many2one(comodel_name='res.currency', domain=[ ('active', '=', True)],string=" ", help = " ")
    domestic_rate = fields.Float(string='Domestic rate', help="")
    domestic_rate_cuurency = fields.Many2one(comodel_name='res.currency', domain=[ ('active', '=', True)],string=" ", help = " ")
    insurance_cost = fields.Float(string='Insurance cost', help="", )
    insurance_cost_currency = fields.Many2one(comodel_name='res.currency', domain=[ ('active', '=', True)],string=" ", help = " ")
    cfee = fields.Float(string='CFEE', help="", )
    cfee_currency = fields.Many2one(comodel_name='res.currency', domain=[ ('active', '=', True)],string=" ", help = " ")
    free_service_cost = fields.Float(string='free service cost', help="", )
    free_service_cost_currency = fields.Many2one(comodel_name='res.currency', domain=[ ('active', '=', True)],string=" ", help = " ")
    lock_margin = fields.Boolean(string="Lock margin")
    has_qrate = fields.Boolean(string="Has QRate")
    currency_ids = fields.One2many('currency.line', 'freight_quotation_id', 'Currency set', default=compute_currency_values)
    is_send_email = fields.Boolean(string="Email send", default=False)
    is_confirmed = fields.Boolean(string="Confirmed", default=False)
    is_active_view = fields.Boolean(string="Active", default=False)
    im_editable = fields.Integer(default=0, compute='compute_im_editable') #
    picked_bool = fields.Boolean(default=False) 
    total_cost = fields.Float(string='Cost', help="Total cost")
    total_rate = fields.Float(string='Rate', help="Total rate", readonly=False,)
    margin=fields.Float(string='Cost',help="Total margin")
    state_id = fields.Selection(selection=[
            ('started', 'Started'),
            ('filled', 'Filled'),
            ('re-cost', 'Re-cost'),
            ('re-inquiry', 'Re-inquiry'),
            ('ready', 'Ready'),
            ('sent', 'Sent'),
            ('confirmed', 'Confirmed'),
            ('cancelled', 'Cancelled'),
        ],
        domain=lambda self: [('state_type.name', 'in', self.compute_state_types())],
        default='started')

    
    base_currency = fields.Many2one(comodel_name='res.currency', string="Currency", domain=[('active', '=', True)], default=lambda self: self.env.company.currency_id) #compute='_compute_currency'
    show_tara = fields.Boolean(default=False)
    show_volgross = fields.Boolean(default=False)
    show_coc = fields.Boolean(default=False)

    
    fcl_route_domain = fields.Char(compute="_compute_domain_fcl_route", readonly=True, default=_get_default_domain_fcl_route)
    taras_domain = fields.Char(compute="_compute_domain_taras", readonly=True,  default=_get_default_domain_taras)

    has_tir = fields.Boolean(string="Has TIR", default=False)
    showhasTir = fields.Boolean(default=False)
    cc_at_border = fields.Boolean(string="CC At Border", default=False)
    is_thc=fields.Boolean(string="THC" , defualt=False)
    storage=fields.Boolean(string="Storage" , defualt=False)
    clear_service=fields.Boolean(string="Clearance Service" , defualt=False)
    from_declaration=fields.Boolean(string="Form Declaration Cost" , defualt=False)
    from_cost=fields.Boolean(string="Form Cost" , defualt=False)
    clearance_fee=fields.Boolean(string="Clearance Fee" , defualt=False)
    item_qty=fields.Integer(string="Item Qty",required=True)
    days_data=fields.Integer(string="Days",required=True)
    custom_rate=fields.Many2one(comodel_name='customers.rates', string="Custom")
    base_id=fields.Char()
    confirm_active = fields.Boolean('Active_Cancel', default=True, tracking=True)
    checker = fields.Boolean(related='freights_id.state_checker')

    quotation_data=fields.Char(compute='_compute_service_data')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, default=lambda self: self.env.company)

    color = fields.Integer('Color Index', default=1)

    employee = fields.Many2one('hr.employee', string="Created by", default=_get_employee_id, readonly=True, required=True, help="Захиалга өгсөн менежерийн нэр")
    changed_domestic=fields.Boolean(string="Clearance Service" , defualt=False)
    changed_abroad=fields.Boolean(string="Clearance Service" , defualt=False)

    demmurage_rates = fields.One2many('freight.demurrages.rates', 'freight_quotation_id', 'Demmurages')
    is_sales = fields.Boolean(default=_get_check_is_sale) 
    is_pd = fields.Boolean(default=_get_check_is_pd) 
    warning_message = fields.Char(readonly=True )

    @api.depends('freights_id.volume', 'gross')
    def _compute_chargable_weight(self):
        freight = self.env["mlworldwide.freights"].browse(self.env.context.get('default_freight_id'))
        res = 0
        if not freight.id:
            freight = self.freights_id
        for rec in self:
            if rec.freights_type_ids.id:
                typname = str(rec.freights_type_ids.type_name).upper()
                if typname == "AIR":
                    res = max([rec.cbm * 167, rec.gross])
                else:
                    print(freight.gross,'-------',freight.gross / 1000)
                    #  Math.max(1, Math.max(volume, grossWeight / kgPerVolume))
                    res = max(1, max(freight.volume , freight.gross / 1000))
            else:
                res = max(1, max(freight.volume , freight.gross / 1000))
            rec.chargabel_weight = res
    
    @api.model
    def create(self, values):
        print("wwwwwwwwwwwwwwwwww", values)
        if 'freights_id' in values:
            freight = self.env["mlworldwide.freights"].search([('id','=', values['freights_id'])])
            employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
            freight_type=self.env["freights.type"].search([('id','=',values['freights_type_ids'])])
            checker = False
            for rec in freight_type:
                freight_type_role = []
                employee = []
                for res in freight.contributor_ids:
                    employee.append(res.employee.id)
                    freight_type_role.append(res.role_name)
                # zasna 
                employee_role = self.env['freights.employee.role'].search([('role_name', '=', rec.type_name)])
                for res in employee_role:
                    if employee_rec.id == res.employee.id:
                        checker = True
                if not (rec.type_name not in freight_type_role and employee_rec.id not in employee):
                    if not checker:                        
                        freight.contributor_ids += self.env['freights.employee.role'].sudo().create({
                            'role_name':rec.type_name,
                            'employee':employee_rec.id
                        })
                    else:
                        freight.contributor_ids += employee_role
            result = super(FreightsQuotationsModel, self).create(values)
            start = freight.origin_point_id.id
            end = freight.destination_point_id.id
            shgowmsg = False
            for rec in self.service_ids:
                abroad_rate = 0
                if rec.show_qrate:
                       abroad_rate += rec.total_qrate
                if (rec.type.id == 1 or rec.type.id == 3) and rec.service_to.id == end:
                    shgowmsg = True
            print(shgowmsg)
            if not shgowmsg:
                result.warning_message = "Insert all freight costs"
            else: 
                result.warning_message = ""
            print("qqqqqqqqqqqqqqqqqqqqqqqqqq")
            if result.has_qrate or result.freights_type_ids.type_name.upper() == 'AIR':    
                result.abroad_rate = abroad_rate
                result.abroad_rate_currency = self.env.company.currency_id
            return result
    
    def write(self, values):
        print("self",self, self.freights_id)
        start = self.freights_id.origin_point_id.id
        end = self.freights_id.destination_point_id.id
        print(end)
        shgowmsg = False
        for rec in self.service_ids:
            abroad_rate = 0
            if rec.show_qrate:
                    abroad_rate += rec.total_qrate
            print(rec.type, rec.service_to.id)
            if (rec.type.id == 1 or rec.type.id == 3) and rec.service_to.id == end:
                shgowmsg = True
        print(shgowmsg)
        if not shgowmsg:
            values['warning_message'] = "Insert all freight costs"
        else: 
            values['warning_message'] = ""
        print("qqqqqqqqqqqqqqqqqqqqqqqqqq")
        if self.has_qrate or self.freights_type_ids.type_name.upper() == 'AIR':    
            values['abroad_rate'] = abroad_rate
            values['abroad_rate_currency'] = self.env.company.currency_id

        return super(FreightsQuotationsModel, self).write(values)
    
    @api.onchange("shipping_line","container_owner","demmurage_start_point","taras_ids","demmurage_end_point")
    def get_demmurafe_rates(self):
        print("hi")
        if self.shipping_line and self.container_owner and self.taras_ids and self.demmurage_start_point and self.demmurage_end_point:
            print("ho")
            if self.demmurage_rates:
                self.demmurage_rates = [(5,0,0)]
            rates = self.env['demurrages.rates'].search([('sline', '=', self.shipping_line.id), 
                                                         ('agent_data', '=', self.container_owner.id),
                                                         ('taras_id', '=', self.taras_ids.id)
                                                    ,('start_point', '=', self.demmurage_start_point.id)
                                                    ,('end_point', '=', self.demmurage_end_point.id)], order="end_date DESC") 
            if rates:
                print(rates)
                currency_lines = []
                for rate in rates:
                    print(rate.start_date, rate.end_date)
                    print(datetime.today())
                    now = datetime.today()
                    if rate.start_date <= now <= rate.end_date:
                        self.free_days = rate.freedays
                        newcurr_line = self.env["freight.demurrages.rates"].sudo().create({'lowerdays': rate.lowerdays,
                                'upperdays': rate.upperdays,
                                'service_rate': rate.service_rate,
                                'currency_id': rate.currency_id.id,
                                'freight_quotation_id': self.id,
                                'freight_id': self.freights_id.id})
                        currency_lines.append(newcurr_line.id)
                self.demmurage_rates = currency_lines
            else:
                self.free_days = 0

  
    @api.onchange("service_ids")
    def calc_ett_min_valid_date(self):
        ett = 0
        valid_date = date.max
        for record in self:
            for shs in record.service_ids:
                if shs.ett:
                    ett += shs.ett
                if shs.valid_until_date and shs.valid_until_date < valid_date:
                    valid_date = shs.valid_until_date
            if date.max != valid_date:
                record.valid_until_date = valid_date
            record.ett_min = ett

    @api.depends('service_ids')
    def _compute_service_data(self):
        for record in self:
            q =""
            for shs in record.service_ids:
                if shs.agent_id.id:
                    q += shs.agent_id.name +":"+str(shs.service_cost) or ""
                    if record.service_ids[len(record.service_ids)-1] != shs:
                        q += '||'
            
            record.quotation_data = q    

    def action_create_custom(self):
        freight = self.env["mlworldwide.freights"].search([("freights_quotations.id" , '=', self.id)])
        custom = self.env["customers.rates"].search([])
        agent=self.env["res.partner"].search([])
        a = 0
        b = 0
        aw=0
        bw=0
        ad=0
        sw = 1+math.ceil((self.item_qty-1)/12)
        c = 1+math.ceil((self.item_qty-1)/12)
        aa=False
        for terminal in custom:
            if terminal.point_data.name == freight.terminal_id.name:
                if self.from_declaration == True and self.item_qty >= terminal.to_data  and terminal.from_data >= self.item_qty and terminal.service_data == 'Гаалийн мэдүүлэг шивэлтийн хөлс':
                    if  terminal.type_data == 'нэмэлт':
                        # if terminal.type_data == 'нэмэлт': 
                            a=terminal.cost_data
                    if  terminal.type_data == 'Үндэс':
                        b=terminal.cost_data  
                    
                    if self.from_declaration == True and terminal.from_data >= self.item_qty and self.item_qty >= terminal.to_data and terminal.type_data == 'нэмэлт':
                        for rc in agent:
                            if rc.name == 'MLW':
                                service_type = self.env['service.types'].search([('purpose', '=', 'Form Declaration Cost')]) 
                                service=self.env['freights.service'].create({
                                        'type':5,
                                        'purpose_radio':service_type.id,
                                        'purpose': 'Form Declaration Cost ',
                                        'service_cost':a+(self.item_qty-1)*b ,
                                        'agent_id': rc.id 
                                })
                                self.service_ids +=service      
                if self.clearance_fee == True:
                    if terminal.package_data== 'мэдүүлгийн маягтын үнэ/12 нэр төрөл тутамд':
                        if terminal.type_data == 'нэмэлт': 
                            aw=terminal.cost_data
                        if terminal.type_data == 'Үндэс':
                            bw=terminal.cost_data 
                        if terminal.service_data =='Гаалийн мэдүүлэг шивэлтийн хөлс' and terminal.package_data== 'мэдүүлгийн маягтын үнэ/12 нэр төрөл тутамд'and terminal.type_data == 'нэмэлт' :
                            for rc in agent:
                                if rc.name == 'MLW':   
                                    service_type = self.env['service.types'].search([('purpose', '=', 'Clearance Fee')]) 
                                    service=self.env['freights.service'].create({
                                            'type':5,
                                            'purpose_radio':service_type.id,
                                            'purpose': 'Clearance Fee ',
                                            'service_cost':aw+(sw-1)*bw,
                                            'agent_id': rc.id 
                                    })
                                    self.service_ids +=service  
                if self.from_cost == True  and self.item_qty >= terminal.to_data  and terminal.from_data >= self.item_qty and terminal.service_data == 'Гаалийн мэдүүлэг шивэлтийн хөлс' and terminal.type_data == 'Үндэс':
                    c=terminal.cost_data
                    for rc in agent:
                        if rc.name == 'MLW': 
                            service_type = self.env['service.types'].search([('purpose', '=', 'Form Cost')])
                            service=self.env['freights.service'].create({
                                'type':5,
                                'purpose_radio': service_type.id,
                                'purpose': 'Form Cost ',
                                'service_cost':c*self.item_qty,
                                'agent_id': rc.id 
                        })
                            self.service_ids +=service    
                if self.clear_service == True and  terminal.service_data =='Брокерийн үйлчилгээ':
                    ad=terminal.cost_data  
                    if self.clear_service == True :           
                        for rc in agent:
                            if rc.name == 'MLW':
                                service_type = self.env['service.types'].search([('purpose', '=', 'Clearance Service')])
                                service=self.env['freights.service'].create({
                                    'purpose': 'Clearance Service',
                                    'type':5,
                                    'purpose_radio': service_type.id,
                                    'service_cost': ad*1 ,
                                    'agent_id': rc.id 
                                })
                                self.service_ids +=service   
                                        
    def action_create_thc(self):
        freight = self.env["mlworldwide.freights"].search([("freights_quotations.id" , '=', self.id)], limit=1)
        ths = self.env["ths.rates"].search([])
        agent=self.env["res.partner"].search([])
        b = 0
        a = 0
        for thc in ths:
            if self.is_thc == True :
                if freight.terminal_id.name == thc.terminal.name and self.freights_type_ids.type_name == thc.type_data.type_name:
                    if self.taras_ids.name == thc.taras_id.name and self.container_type.name == thc.container.name :
                        if thc.service_type == 'THC':
                            a = thc.cost_data
                        for rc in agent:
                            if rc.name == 'MLW':
                                service_type = self.env['service.types'].search([('purpose', '=', 'THC')])
                                service=self.env['freights.service'].create({
                                    'type':4,
                                    'purpose_radio':service_type.id,
                                    'purpose': 'THC ',
                                    'service_cost': a*self.days_data ,
                                    'agent_id': rc.id 
                                })
                                self.service_ids +=service    
            if self.storage == True :  
                if freight.terminal_id.name == thc.terminal.name and self.freights_type_ids.type_name == thc.type_data.type_name and self.taras_ids.name == thc.taras_id.name and  thc.service_type == 'Storage':
                    b = thc.cost_data
                    for rc in agent:
                        if rc.name == 'MLW':
                            service_type = self.env['service.types'].search([('purpose', '=', 'Storage')])
                            service=self.env['freights.service'].create({
                            
                                
                                'purpose': 'Storage',
                                'type':4,
                                'purpose_radio':service_type.id,
                                'service_cost': b*self.days_data ,
                                'agent_id': rc.id 
                            })
                            self.service_ids +=service                                    

    def _compute_domain_taras(self):
        for rec in self:
            res = []
            for ttype in rec.freights_id.taras_id:
                res.append(ttype.id)
            rec.taras_domain = json.dumps([('id', 'in', res)])

    def _compute_domain_freight_type(self):
        for rec in self:
            print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
            freight = self.env["mlworldwide.freights"].browse(self.env.context.get('default_freight_id'))
            print(freight)
            res = []
            for ttype in freight.freigths_type:
                res.append(ttype.id)
            rec.freight_type_domain = json.dumps([('id', 'in', res)])

    def _compute_domain_fcl_route(self):
        for rec in self:
            res = []
            for ttype in rec.freights_id.fclroute_ids:
                res.append(ttype.id)
            rec.fcl_route_domain = json.dumps([('id', 'in', res)])
    
    @api.model
    def default_get(self, default_fields):
        res = super(FreightsQuotationsModel, self).default_get(default_fields)
        fid = self._context.get('default_freight_id')
        return res

    # def _compute_service_ids(self):
    #     if self.freights_id.has_insurance:
    #         insurance_cost = self.env['insurance.cost'].search([('freight_type', '=', self.freights_type_ids.id)], limit=1)
    #         self.service_ids += self.env['freights.service'].create({
    #             'currency_id' : insurance_cost.cost_currency.id,
    #             'service_cost' : insurance_cost.cost
    #         })
    @api.onchange("gross","cbm")
    def _onchagne_gross_cbm(self):
        self._compute_chargable_weight()

    @api.onchange("container_type")
    def _onchange_container_type(self):
        coc = False
        typname = str(self.container_type.name).upper()
        if typname == "COC":
            coc = True
        self.show_coc = coc

    @api.onchange("base_currency")
    def _onchange_action_rate(self):
        self._calc_exchange_rate()
        # if self.currency_ids:
        #     base_sell =1
        #     tmp = []
        #     for line in self.currency_ids:
        #         if line.currency_id.name == self.base_currency.name:
        #             base_sell = line.sell

        #     for line in self.currency_ids:
        #         currency_rate = line.sell
        #         currency_rate_buy = line.buy
        #         if currency_rate is not None and currency_rate_buy is not None and self.base_currency:
        #             rate = 1
        #             if line.currency_id.name != self.base_currency.name:
        #                 rate = base_sell / currency_rate
        #             line.update({'rate': rate})
            #         tmp.append(line)
            # self.currency_ids = tmp
        self.compute_total_cost()
        self.compute_total_rate()
        self.compute_total_margin()
    
    def _calc_exchange_rate(self):
        if self.currency_ids:
            base_sell =1
            tmp = []
            for line in self.currency_ids:
                if line.currency_id.name == self.base_currency.name:
                    base_sell = line.sell

            for line in self.currency_ids:
                currency_rate = line.sell
                currency_rate_buy = line.buy
                if currency_rate is not None and currency_rate_buy is not None and self.base_currency:
                    rate = 1
                    if line.currency_id.name != self.base_currency.name:
                        rate = base_sell / currency_rate
                    line.update({'rate': rate})        

    @api.onchange('fclroute_ids')
    def _fclroute_ids_onchange(self):
        self.calc_include_exclude_servcie()
        # freights_incexc_temp = self.env["freight.incexc.service.template"].search([])
        # is_include = False
        # for record in freights_incexc_temp:
        #     f_type = self.freights_type_ids
        #     if f_type.id:
        #         if f_type.type_name.lower() == "fcl":
        #             for fcl_rout in self.fclroute_ids:
        #                 if fcl_rout.name.lower() == "via xg":
        #                     if fcl_rout in record.fcl_route:
        #                         is_include= True
        #                 if fcl_rout.name.lower() == "via riga":
        #                     if fcl_rout in record.fcl_route:
        #                         is_include= True
        #                 if fcl_rout.name.lower() == "via klaipeda":
        #                     if fcl_rout in record.fcl_route:
        #                         is_include= True
        #         elif f_type.type_name.lower() == "ltl":
        #             if f_type in record.incexc_freight_types:
        #                     is_include= True
        #     if is_include:
        #         self.env["freight.incexc.service"].create({
        #             'name':str(record.name),
        #             'quotation_id':self.id,
        #             'isincluded': is_include,
        #         })
        #     is_include = False
                        
    @api.onchange("freights_type_ids")
    def _get_include_service_default(self):
        self.calc_insurance_currency()

        res = False
        volgross = False
        hasTir = False
       
        typname = str(self.freights_type_ids.type_name).upper()
        if typname == "FCL":
            res = True
            
        if typname == "LCL" or typname == "LTL" or typname == "AIR" or typname == "TRAIN" or typname == "WGN" or typname == "MULTIMODAL":
            volgross = True
        
        if typname == "FTL":
            hasTir = True

        for rec in self:
            if volgross:
                self.gross = rec.freights_id.gross
                self.cbm = rec.freights_id.volume
        self.show_tara = res
        self.show_volgross = volgross
        self.showhasTir = hasTir

        if typname == "AIR":
            self.has_qrate = True

        typname = str(self.container_type.name).upper()
        coc = False
        if res and typname == "COC":
            coc = True
        self.show_coc = coc

        self.calc_include_exclude_servcie()
        self._compute_chargable_weight()
    
    def calc_include_exclude_servcie(self):
        if self.freights_type_ids:
            if self.freights_incude_service:
                self.freights_incude_service = [(5,0,0)]
                
            if self.freights_exclude_service:
                self.freights_exclude_service = [(5,0,0)]
                 
            freight_base = self.env['mlworldwide.freights'].sudo().browse(self.env.context.get('default_freight_id'))
            
            # freights_incexc_temp = self.env["freight.incexc.service.template"].search([])
            # print(freights_incexc_temp.locale)
            freights_incexc_temp = self.env["freight.incexc.service.template"].search([('locale', '=', freight_base.customer_id.lang)])
            if len(freights_incexc_temp) == 0:
                freights_incexc_temp = self.env["freight.incexc.service.template"].search([])
            

            for record in freights_incexc_temp:
                is_include = False
                if  freight_base.origin_term in record.origin_terms:
                    is_include= True
                if  freight_base.destination_term in record.destination_terms:
                    is_include= True
                for s_types in record.service_types:
                    if s_types:
                        for oneservice in self.service_ids:
                            if not isinstance(oneservice.type, str):
                                if oneservice.type == s_types:
                                    is_include= True
                if record.countries:
                    if freight_base.origin_point_id.country.name != record.countries.name:
                        if record.incexc_freight_types:
                            if record.fcl_route and self.fclroute_ids:
                                if self.fclroute_ids in record.fcl_route:
                                     is_include= True
                            else: 
                                if self.freights_type_ids in record.incexc_freight_types:
                                     is_include= True
                else:   
                    if record.incexc_freight_types:
                        if record.fcl_route and self.fclroute_ids:
                            if self.fclroute_ids in record.fcl_route:
                                    is_include= True
                        else: 
                            if self.freights_type_ids in record.incexc_freight_types:
                                    is_include= True


                # for f_type in self.freights_type_ids:
                #     for bf_type in record.incexc_freight_types:
                #         if bf_type:
                #             if f_type.type_name.lower() == bf_type.type_name.lower():
                #                 is_include= True
                # if freight_base.origin_term.code == "EXW":
                #     if  freight_base.origin_term in record.origin_terms:
                #         is_include= True
                # if freight_base.origin_term.code == "FCA":
                #     if  freight_base.origin_term in record.origin_terms:
                #         is_include= True
                # if freight_base.destination_term.code == "DAP":
                #     if  freight_base.destination_term in record.destination_terms:
                #         is_include= True
                # if freight_base.destination_term.code == "DDP":
                #     if  freight_base.destination_term in record.destination_terms:
                #         is_include= True
                # if freight_base.destination_term.code == "DDU":
                #     if  freight_base.destination_term in record.destination_terms:
                #         is_include= True
                # is_s_type = ""
                # for s_types in record.service_types:
                #     if s_types.name == "Custom":
                #         is_s_type = "Custom"
                #     if s_types.name == "THC":
                #         is_s_type = "THC"
                #     if s_types.name == "Deliver":
                #         is_s_type = "Deliver"    
                # if is_s_type != "":
                #     for service in self.service_ids:
                #         if not isinstance(service.type, str):
                #             if service.type == is_s_type:
                #                 is_include= True
                # if freight_base.origin_point_id.country.name != "china":
                #     for f_type in self.freights_type_ids:
                #         if f_type.type_name.lower() == "air":
                #             if f_type in record.incexc_freight_types:
                #                 is_include= True
                #         if f_type.type_name.lower() == "lcl":
                #             if f_type in record.incexc_freight_types:
                #                 is_include= True
                #         if f_type.type_name.lower() == "multimodal":
                #             if f_type in record.incexc_freight_types:
                #                 is_include= True

                
                # if  (len(record.destination_terms) == 0 and len(record.origin_terms) == 0  and len(record.fcl_route) == 0 and len(record.incexc_freight_types)== 0 ):
                #     service = self.env["freight.incexc.service"].create({
                #         'name':str(record.name),
                #         'quotation_id':self.id,
                #         'isincluded': is_include,
                #     })
                # elif is_include:
                service = self.env["freight.incexc.service"].create({
                    'name':str(record.name),
                    'quotation_id':self.id,
                    'isincluded': is_include,
                })
       
    def calc_insurance_currency(self):
        if self.freights_id.has_insurance and self.freights_type_ids.id:
            insurance_cost_tmp = self.env['insurance.cost'].search([('freight_type', '=', self.freights_type_ids.id)], limit=1)
            self.insurance_cost = insurance_cost_tmp.cost
            self.insurance_cost_currency = insurance_cost_tmp.cost_currency.id
            for record in self:
                for exchange in record.currency_ids:
                    if insurance_cost_tmp.cost_currency:
                        if insurance_cost_tmp.cost_currency.id == exchange.currency_id.id and exchange.currency_id.id != self.base_currency.id:
                            self.insurance_cost = self.insurance_cost / exchange.rate
                            self.insurance_cost_currency = self.base_currency.id

    @api.onchange("service_ids")
    def total_calc(self):
        self.compute_total_cost()
        self.compute_total_rate()
        self.compute_total_margin()

    @api.onchange("total_rate", "total_cost")
    def _onchange_compute(self):
        self.compute_total_margin()

    def compute_total_margin(self):
        total= 0
        # freight = self.freights_id
        freight = self.env["mlworldwide.freights"].browse(self.env.context.get('default_freight_id'))
        
        if not freight.id:
            freight = self.freights_id
        # if freight.id:
        # self.freights_type_ids=freight.freigths_type[0].id
       
        for rec in self:
            if not rec.lock_margin:
                # total += rec.total_rate - rec.total_cost
                # if rec.abroad_rate:
                #     total -=  rec.abroad_rate
                #     rec.domestic_rate = total
                # elif rec.domestic_rate:
                #     total -= rec.domestic_rate
                #     rec.abroad_rate = total

                # total += rec.total_rate - rec.margin - rec.abroad_rate
                # rec.domestic_rate = round(total, 2)
            # else:
                total += rec.total_rate -  rec.total_cost
                rec.margin = round(total, 2)

            # for service in rec.service_ids:
            #     if service.currency_id == rec.env.company.currency_id:
            #         total += service.service_rate -  service.service_cost
    
    @api.onchange("cfee","free_service_cost","insurance_cost",'cfee_currency', 'insurance_cost_currency', 'free_service_cost_currency')
    def calc(self):
        self.compute_total_cost()
        self.compute_total_margin()

    def compute_total_cost(self):
        self.ensure_one()
        total = 0

        self.calc_insurance_currency()

        if self.insurance_cost_currency:
            if self.base_currency.id == self.insurance_cost_currency.id:
                print(self.base_currency.name, self.insurance_cost_currency.name)
                total += self.insurance_cost

        if self.cfee_currency:
            if self.base_currency.id == self.cfee_currency.id:
                total += self.cfee

        if self.free_service_cost_currency:
                    if self.base_currency.id == self.free_service_cost_currency.id:
                        total += self.free_service_cost

        for service in self.service_ids:
            if service.currency_id.id == self.base_currency.id:
                total += service.service_cost
        for record in self:
            for exchange in record.currency_ids:

                if self.insurance_cost_currency:
                    if self.insurance_cost_currency.id == exchange.currency_id.id and exchange.currency_id.id != self.base_currency.id:
                        print(self.base_currency.name, self.insurance_cost_currency.name,  exchange.rate, "dfasdfasd")
                        total += self.insurance_cost / exchange.rate

                if self.cfee_currency:
                    if self.cfee_currency.id == exchange.currency_id.id and exchange.currency_id.id != self.base_currency.id:
                        total += self.cfee / exchange.rate
                        
                if self.free_service_cost_currency:
                            if self.free_service_cost_currency.id == exchange.currency_id.id and exchange.currency_id.id != self.base_currency.id:
                                total += self.free_service_cost / exchange.rate

                for service in self.service_ids:
                    if service.currency_id.id == exchange.currency_id.id and service.currency_id.id != self.base_currency.id:
                        total += service.service_cost / exchange.rate
        # if not self.lock_margin:
        self.total_cost = round(total, 2)

    @api.onchange('abroad_rate','abroad_rate_currency')
    def _compute_lock_margin_domestic_rate(self):
        self._calc_exchange_rate()
        total = 0
        
        if self.total_rate:
            if self.lock_margin:
                self.changed_abroad = True
                total += self.total_rate - self.total_cost
                print("self.changed_domesticv", self.changed_domestic)
                if not self.changed_domestic:
                    if self.abroad_rate_currency:
                        abroad = 0
                        for exchange in self.currency_ids:
                            if exchange.currency_id.id == self.abroad_rate_currency.id:
                                print("self.abroad_rate", self.abroad_rate)
                                abroad += self.abroad_rate / exchange.rate
                                total -= abroad
                                for ret in self.currency_ids:
                                    if ret.currency_id.id == self.domestic_rate_cuurency.id:
                                        self.domestic_rate = total * ret.rate
                    else:
                        total -= self.abroad_rate
                        self.domestic_rate_cuurency = self.base_currency.id
                        self.abroad_rate_currency = self.base_currency.id
                        self.domestic_rate = total
                    print("self.changed_domesticv", self.domestic_rate)
                self.changed_domestic = False

        self.compute_total_rate()
        print("self.changed_domesticv", self.domestic_rate)
        self.compute_total_margin()
        print("self.changed_domesticv", self.domestic_rate)

    @api.onchange('domestic_rate','domestic_rate_cuurency')
    def _compute_domestic_rate(self):
        total = 0
        print("self.changed", self.domestic_rate)
        self._calc_exchange_rate()
        if self.domestic_rate and self.lock_margin:
            self.changed_domestic = True
            total += self.total_rate - self.total_cost
            abroad = 0
            print("self.changed", self.changed_abroad)
            print("self.changed", self.domestic_rate)
            if  not self.changed_abroad:
                for exchange in self.currency_ids:
                    if exchange.currency_id.id == self.domestic_rate_cuurency.id:
                        abroad += self.domestic_rate / exchange.rate
                        total -= abroad
                        for ret in self.currency_ids:
                                if ret.currency_id.id == self.abroad_rate_currency.id:
                                    self.abroad_rate = total * ret.rate
            self.changed_abroad = False
        self.compute_total_rate()
        self.compute_total_margin()

    def compute_total_rate(self):
        self.ensure_one()
        total = 0
        self._calc_exchange_rate()
        if self.freights_type_name:
            if str(self.freights_type_name).upper() != "AIR":
                if self.abroad_rate_currency:
                    if self.base_currency.id == self.abroad_rate_currency.id:
                        total += self.abroad_rate


                if self.domestic_rate_cuurency:
                    if self.base_currency.id == self.domestic_rate_cuurency.id:
                        total += self.domestic_rate
        print("total", total)
        for service in self.service_ids:
            if service.currency_id.id == self.base_currency.id:
                total += service.service_rate
        for record in self:
            for exchange in record.currency_ids:
                print(exchange.currency_id.name, exchange.rate, self.base_currency.name)
                if str(self.freights_type_name).upper() != "AIR":
                    if self.abroad_rate_currency:
                        if self.abroad_rate_currency.id == exchange.currency_id.id and exchange.currency_id.id != self.base_currency.id:
                            total += self.abroad_rate / exchange.rate

                    if self.domestic_rate_cuurency:
                        if self.domestic_rate_cuurency.id == exchange.currency_id.id and exchange.currency_id.id != self.base_currency.id:
                            print(exchange.rate, self.domestic_rate_cuurency.name)
                            total += self.domestic_rate / exchange.rate

                for service in self.service_ids:
                    if service.currency_id.id == exchange.currency_id.id and service.currency_id.id != self.base_currency.id:
                        total += service.service_rate / exchange.rate
        print("total", total)
        if not self.lock_margin:
            self.total_rate = round(total, 2)

        if str(self.freights_type_name).upper() == "AIR":
            self.abroad_rate = round(total, 2)
            self.abroad_rate_currency = self.base_currency
            self.domestic_rate_cuurency = self.base_currency


    @api.onchange('state_id')
    def _onchange_state_id(self):
        # body = ""
        # self.env['mail.channel'].search([('id','=',15)],limit=1).message_post(author_id=self.env.user.partner_id.id, body='ashdkas dkuahsdk jashdk jas', message_type='notification', content_subtype='plaintext')

        # arr = []
        # for ugroup in self.env['hr.employee'].search([('user_id', '=', self.env.user.id)]).user_groups:
        #     arr.append(ugroup.name.lower())

        if self._origin.state_id: 
            # for quotation in self.freights_id.freights_quotations:
            #     # if quotation.state_id == 'confirmed':
            #     #     raise ValidationError('Confirmed quotation exists')

            if self._origin.state_id == 'started':
                if (self.user_has_groups('ml_worldwide-main.group_mlworldwide_pd_manager') or self.user_has_groups('ml_worldwide-main.group_mlworldwide_pd')):
                    if self.state_id != 'filled' and self.state_id != 're-inquiry'  and self.state_id != 'cancelled':
                        raise ValidationError("Its not possible")
                    elif self.state_id == 'filled':
                        contributor_store = self.env['hr.employee'].search([('id', '=', -1)])
                        for contributor in self.freights_id.contributor_ids:
                            if contributor.employee.user_id.has_group('ml_worldwide-main.group_mlworldwide_sales') or contributor.employee.user_id.has_group('ml_worldwide-main.group_mlworldwide_manager'):
                                contributor_store+=contributor.employee
                        self.send_notification(contributor_store, datetime.now(), datetime.now()+timedelta(seconds=1000) ,'Quotation state changed into filled', 'Quotation state changed into filled', 'message')
                    elif self.state_id == 're-inquiry':
                        contributor_store = self.env['hr.employee'].search([('id', '=', -1)])
                        for contributor in self.freights_id.contributor_ids:
                            if contributor.employee.user_id.has_group('ml_worldwide-main.group_mlworldwide_sales') or contributor.employee.user_id.has_group('ml_worldwide-main.group_mlworldwide_manager'):
                                contributor_store+=contributor.employee
                        self.send_notification(contributor_store, datetime.now(), datetime.now()+timedelta(seconds=1000) ,'Quotation state changed into re-inquiry', 'Quotation state changed into re-inquiry', 'message')
                elif (self.user_has_groups('ml_worldwide-main.group_mlworldwide_sales') or self.user_has_groups('ml_worldwide-main.group_mlworldwide_manager')):
                    if self.state_id != 're-cost':
                        raise ValidationError("You don't have permission to change the state")
                else:
                    raise ValidationError("You don't have permission to change the state")
            if self._origin.state_id == 'filled':
                if (self.user_has_groups('ml_worldwide-main.group_mlworldwide_sales') or self.user_has_groups('ml_worldwide-main.group_mlworldwide_manager')):
                    if self.state_id != 'ready' and self.state_id != 're-cost' and self.state_id != 'cancelled': 
                        raise ValidationError("Its not possible")
                    elif self.state_id == 're-cost':
                        # employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
                        # for group in employee.user_groups:
                        #     if group.name.lower() == 'pd':
                        grouped_country = self.env['res.country.group'].search([('name', '=', 'Asia')], limit=1)
                        if self.freights_id.freights_route[0].point.name in grouped_country.country_ids.name:
                            end_date = self.get_due_date(datetime.now(), 8)
                            self.freights_id.date_store = end_date['end_date']
                        else:
                            end_date = self.get_due_date(datetime.now(), 16)
                            self.freights_id.date_store = end_date['end_date']

                        contributor_store = self.env['hr.employee'].search([('id', '=', -1)])
                        for contributor in self.freights_id.contributor_ids:
                            if contributor.employee.user_id.has_group('ml_worldwide-main.group_mlworldwide_pd_manager') or contributor.employee.user_id.has_group('ml_worldwide-main.group_mlworldwide_pd'):
                                contributor_store+=contributor.employee
                        self.send_notification(contributor_store, datetime.now(), datetime.now()+timedelta(seconds=1000) ,'Quotation state changed into re-cost', 'Quotation state changed into re-cost', 'message')
                else:
                    raise ValidationError("You don't have permission to change the state")
            if self.state_id == 'ready':
                if not self.ett_max:
                    raise ValidationError("You must fill ett max field")
            if self._origin.state_id == 'ready':
                if (self.user_has_groups('ml_worldwide-main.group_mlworldwide_sales') or self.user_has_groups('ml_worldwide-main.group_mlworldwide_manager')):   
                    if self.state_id != 'cancelled' and self.state_id != 'confirmed':
                        raise ValidationError("Its not possible")
                else:
                    raise ValidationError("You don't have permission to change the state")

            if self._origin.state_id == 're-cost':
                if (self.user_has_groups('ml_worldwide-main.group_mlworldwide_pd_manager') or self.user_has_groups('ml_worldwide-main.group_mlworldwide_pd')):
                    if self.state_id != "filled" and self.state_id != 'cancelled':
                        raise ValidationError("Its not possible")
                else:
                    raise ValidationError("You don't have permission to change the state")

            if self._origin.state_id == 'sent' and self.state_id != 'cancelled':
                    raise ValidationError("Its not possible")

            if self._origin.state_id == 're-inquiry':
                if (self.user_has_groups('ml_worldwide-main.group_mlworldwide_pd_manager') or self.user_has_groups('ml_worldwide-main.group_mlworldwide_pd')):
                    if self.state_id != "started"  and self.state_id != 'cancelled':
                        raise ValidationError("Its not possible")
                else:
                    raise ValidationError("You don't have permission to change the state")

            if self._origin.state_id == 'confirmed' or self._origin.state_id == 'cancelled':
                    raise ValidationError("Its not possible")

            if self.state_id == 'confirmed':
                for rec in self.freights_id.freights_quotations:
                    if rec.picked_bool == True:
                        raise ValidationError(_("Already picked quotation!"))

                self.picked_bool = True
                self.freights_id.route_shipment_boolean = True

       

    def send_notification(self, partners, start_date, end_date, title, body, type):
        starttime =start_date.strftime('%Y-%m-%d %H:%M:%S')
        endtime = end_date.strftime('%Y-%m-%d %H:%M:%S')
        if type == "meeting":
            self.create_event_activity(starttime, endtime, title, body, type)
        if type == "notification":
            return self.create_notification(title, body, type) 
        if type == "message":
            self.create_message(partners, body)    

    def create_event_activity(self, start_date, end_date, title, body, type):
        activty_type = self.env['mail.activity.type'].search([('category','=',type)], limit = 1)

        if len(activty_type) == 0:
            activty_type = self.env['mail.activity.type'].create({
                'name': str(type).capitalize(),
                'category': str(type).lower()
            })

        activity_id = self.env['mail.activity'].create({
            'summary': str(title).capitalize(),
            'activity_type_id': activty_type.id,
            'res_model_id': self.env['ir.model']._get_id('mlworldwide.freights'),
            'res_id': self.id,  #self.env['res.partner'].create({'name': 'A Partner'}).id,
        })

        calendar_event = self.env['calendar.event'].create({
            'name': str(title).capitalize(),
            'activity_ids': [(6, False, activity_id.ids)],
            'start': start_date,
            'stop': end_date,
        })

        # Check output in the user's tz
        # write on the event to trigger sync of activities
        calendar_event.with_context({'tz': 'Asia/Ulaanbaatar'}).write({
            'start': start_date, #'2022-12-30 21:00:00',
        })
    def create_notification(self, title, body, type):
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'warning',
                'title': title,
                'message': body,
                'sticky': False,
                }
        }
        return notification

    def create_message(self, partners, body):
        if self.freights_id.freights_channel_id.channel_partner_ids == partners:
            self.freights_id.freights_channel_id.message_post(body=self.quotation_ref_num +": "+body, message_type='notification')
        else:
            """  Message channel uuseegui bol shineer uusgeed notification yabyylna """
            name = ""
            for partner in partners:
                name += "_" + str(partner.id)
            chnl = self.env['mail.channel'].search([('name','=',self.freights_id.ref_num + name)])
            if not chnl:
                channel = self.env['mail.channel'].sudo().create({
                    'name': '' + self.ref_num + name,
                    'channel_partner_ids': [(4, self.env['res.users'].browse(self.env.user.id).partner_id.id)]
                })
                
                for ps in partners:
                    if ps.user_id:
                        channel.sudo().channel_partner_ids += ps.user_id
                channel.message_post(body=self.quotation_ref_num +": "+body, message_type='notification')    
            else:
                chnl.message_post(body=self.quotation_ref_num +": "+body, message_type='notification')

    def compute_state_types(self):
        result = []
        result.append("Quotation")
        return result
        
    def compute_im_editable(self):
        im_editable = 0
        # if self.freights_id.employee.user_groups:
        if (self.user_has_groups('ml_worldwide-main.group_mlworldwide_pd_manager') or self.user_has_groups('ml_worldwide-main.group_mlworldwide_pd')):
            if self.state_id.lower() == "started":
                im_editable = 1 #pd
            if self.state_id.lower() == "re-cost":
                im_editable = 1 #pd    
        if (self.user_has_groups('ml_worldwide-main.group_mlworldwide_sales') or self.user_has_groups('ml_worldwide-main.group_mlworldwide_manager')):
            if self.state_id.lower() == "filled":
                im_editable = 2 #sale
            if self.state_id.lower() == "ready":
                im_editable = 2 #sale
            
        self.im_editable=im_editable
        return self.im_editable #["Freight", "Quotation"]   

    def compute_name(self):
        last = self.env['freights.quotations'].search([('create_date', 'ilike' , fields.Datetime.now().strftime('%Y-%m')), ('employee', '=', self.employee.id)]) 
        name = "Q/" + str(self.env.user.id) + '/' + str(fields.Datetime.now().year) + '/' + str(fields.Datetime.now().month) + '/' + str(len(last)+1).zfill(5)
        return name

    def _compute_quote_name(self):
        for rec in self:
            rec.quote_name = ''

    def action_get_quotation(self):
        self.ensure_one()
        parent_id = self.id 
        parent_model = self.env.context.get('parent_model') 

    def action_preview_quotation(self):
        # TODO ene Quotationno preview hiideg code
        freight = self.freights_id #self.env["mlworldwide.freights"].browse(self.id)
        report = self.env['ir.actions.report']._get_report_from_name('ml_worldwide-main.mlworldwide_quotation')
        report.report_type = 'qweb-html'
        html = report.report_action(self, config = False)
        return html

    def action_send_quotation_email(self):
        if self.state_id != 'ready': raise ValidationError("Sorry, you can send email when the state is only ready!")
        freight = self.freights_id #self.env["mlworldwide.freights"].browse(self.id)
        template_id = self.env.ref('ml_worldwide-main-main.mlworldwide_quotation_mail').id
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
            
        ctx = {
            'default_model': 'freights.quotations',
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

    # def action_quotation_confrim(self):
    #     self.ensure_one()
    #     if self.margin>0:
    #         result = self.quotation_confrim()
    #         return result
    #     else:
    #         new_wizard = self.env['quotation.margin.confirm'].create({'ref_num':self.quotation_ref_num})
    #         view_id = self.env.ref('ml_worldwide-main.quotation_margin_confirm').id
    #         return {
    #             'type': 'ir.actions.act_window',
    #             'name': 'Confirm',
    #             'view_mode': 'form',
    #             'res_model': 'quotation.margin.confirm',
    #             'target': 'new',
    #             'res_id': new_wizard.id,
    #             'views': [[view_id, 'form']],
    #         }
        
    def quotation_confrim(self):
        agent_mail = self.env['quotation.agents.mail'].search([('id', '=', -1)])

        for service in self.service_ids:
            contacts = self.env['quotation.agents.mail'].search([])
            checker = False
            for rec in contacts:
                if rec.agent.id == service.agent_id.id:
                    checker = True
                    agent_mail += rec

            if not checker:
                agent_contact_mail = self.env['quotation.agents.mail'].create({
                    'agent' : service.agent_id.id,
                    'contacts' : service.agent_id.child_ids,
                    'service_id' : service.id
                })
                agent_mail += agent_contact_mail
        margin = ""
        if self.margin <= 0:
            margin = "Low margin"

        wizard = self.env['quotation.confirm.wizard'].create({
            'shipment_qty' : self.freights_id.shipment_qty,
            'quotation' : self.id,
            'consignee' : self.freights_id.customer_id.id,
            'recipients' : self.freights_id.customer_id,
            'ett_max' : self.ett_max,
            'agent_contact_mails' : agent_mail,
            'text' : margin
        })
        return {
            'name': ('Quotation confirm wizard'),
            'type': 'ir.actions.act_window',
            'res_model': 'quotation.confirm.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new'
        }

    def create_pay(self):
        self.create_payments(self.freights_id, self.service_ids) 

    # TEMPLATE CODE
    # def action_payments(self):
    #     self.create_payments(self.freights_id, self.service_ids)    

    @api.model
    def create_payments(self, freights, quotation):
        # for pservice in freights.freights_payments:
        #     pservice.unlink()
        if freights.freights_shipment:
            for shipment in freights.freights_shipment:
                
                for service in self.service_ids:
                    # pservice = service.copy()s
                    print(freights.customer_id.parent_id)
                    freights.freights_payments += self.env['freights.payment.service'].sudo().create({
                        'payer_id':freights.customer_id.parent_id.id,
                        'agent_id':service.agent_id.id,
                        'service_from':service.service_from.id,
                        'service_to':service.service_to.id,
                        'transport_type':service.transport_type.id,
                        'service_desc':str(service.type.name) + str(service.purpose),
                        'service_qty':1,
                        'currency_id':service.currency_id.id,
                        'service_cost':service.service_cost,
                        'service_rate':service.service_rate,
                        'ett':service.ett,
                        'valid_until_date':service.valid_until_date,
                        'shippment_ids':[shipment.id],
                        'freights_id':freights.id
                    })

                # abroad_rate = fields.Float(string='Abroad rate', help="", )
                # abroad_rate_currency = fields.Many2one(comodel_name='res.currency',string=" ", help = " ")
                # domestic_rate = fields.Float(string='Domestic rate', help="", )
                # domestic_rate_cuurency = fields.Many2one(comodel_name='res.currency',string=" ", help = " ")
                # insurance_cost = fields.Float(string='Insurance cost', help="", )
                # insurance_cost_currency = fields.Many2one(comodel_name='res.currency',string=" ", help = " ")
                # cfee = fields.Float(string='CFEE', help="", )
                # cfee_currency = fields.Many2one(comodel_name='res.currency',string=" ", help = " ")
                # free_service_cost = fields.Float(string='free service cost', help="", )
                # free_service_cost_currency = fields.Many2one(comodel_name='res.currency',string=" ", help = 
                if self.abroad_rate:
                    freights.freights_payments += self.env['freights.payment.service'].sudo().create({
                        'payer_id':freights.customer_id.parent_id.id,
                        'service_desc':"Abroad rate",
                        'service_qty':1,
                        'currency_id':self.abroad_rate_currency.id,
                        'service_cost' : 0,
                        'service_rate':self.abroad_rate,
                        'shippment_ids':[shipment.id],
                        'freights_id':freights.id
                    })
                if self.domestic_rate:
                    freights.freights_payments += self.env['freights.payment.service'].sudo().create({
                        'payer_id':freights.customer_id.parent_id.id,
                        'service_desc':"Domestic rate",
                        'service_qty':1,
                        'currency_id':self.domestic_rate_cuurency.id,
                        'service_cost' : 0,
                        'service_rate':self.domestic_rate,
                        'shippment_ids':[shipment.id],
                        'freights_id':freights.id
                    })
                if self.insurance_cost:
                    freights.freights_payments += self.env['freights.payment.service'].sudo().create({
                        'service_desc':"Insurance cost",
                        'service_qty':1,
                        'currency_id':self.insurance_cost_currency.id,
                        'service_cost' : self.insurance_cost,
                        'service_rate': 0,
                        'shippment_ids':[shipment.id],
                        'freights_id':freights.id
                    })
                if self.cfee:
                    freights.freights_payments += self.env['freights.payment.service'].sudo().create({
                        'service_desc':"CFEE",
                        'service_qty':1,
                        'currency_id':self.cfee_currency.id,
                        'service_cost' : self.cfee,
                        'service_rate': 0,
                        'shippment_ids':[shipment.id],
                        'freights_id':freights.id
                    })
                if self.free_service_cost:
                    freights.freights_payments = self.env['freights.payment.service'].sudo().create({
                        'service_desc':"Free service cost",
                        'service_qty':1,
                        'currency_id':self.free_service_cost_currency.id,
                        'service_cost' : self.free_service_cost,
                        'service_rate': 0,
                        'shippment_ids':[shipment.id],
                        'freights_id':freights.id
                    })

        for rec in freights:
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
                    
    def action_view_quotation(self):
        self.ensure_one()
        freight = self.env["mlworldwide.freights"].browse(self.id)

    def action_remove_quotation(self):
        self.ensure_one()
        freight = self.env["mlworldwide.freights"].browse(self.id)
        freight.freights_quotations -= self

    def action_quoation_email_send(self):
        return True

    def action_open_record(self): 
        return {
            'type': 'ir.actions.act_window', 
            'res_model': 'freights.quotations', 
            'name': 'Record name', 
            'view_type': 'form', 
            'view_mode': 'form', 
            'res_id': self.id, 
            'context':{'default_freights_id': self.freights_id},
            'target': 'current', 
        }

class QuotationMarginConfirm(models.TransientModel):
    _name = 'quotation.margin.confirm'
    _description = 'Quotation margin confirm'

    ref_num = fields.Char(string='Reference',)

    def apply(self):
        return self.env['freights.quotations'].search([('quotation_ref_num', '=', self.ref_num)], limit=1).quotation_confrim()