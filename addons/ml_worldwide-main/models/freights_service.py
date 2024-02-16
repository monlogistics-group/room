# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-12-02
import json
import datetime
from odoo.exceptions import UserError, ValidationError
from email.policy import default
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import date_utils
import json

class FreightsServicesModel(models.Model):
    _name = "freights.service"
    _description = "Worldwide freights service model"
    _order = 'sequence desc'

    def get_default_isWeightable(self):
        quotation = self.env["freights.quotations"].browse(self.env.context.get('default_quotation_id'))
        ft = self.env["freights.type"].browse(self.env.context.get('def_freight_type'))
        print("------------------------------------------------------",ft)
        if ft:
            typname = str(ft.type_name).upper()
            if typname == "LCL" or typname == "LTL" or typname == "AIR" or typname == "TRAIN" or typname == "WGN" or typname == "MULTIMODAL":
                return True
        elif quotation:
            typname = str(quotation.freights_type_ids.type_name).upper()
            if typname == "LCL" or typname == "LTL" or typname == "AIR" or typname == "TRAIN" or typname == "WGN" or typname == "MULTIMODAL":
                return True
        return False
    
    def get_default_qrate(self):
        quotation = self.env["freights.quotations"].browse(self.env.context.get('default_quotation_id'))
        if quotation:
            if quotation.has_qrate or quotation.freights_type_name.upper() == 'AIR':
                return True
        return False
    
    def get_default_modal(self):
        quotation = self.env["freights.quotations"].browse(self.env.context.get('default_quotation_id'))
        print(quotation,'===========quotation')
        if quotation:
            typname = str(quotation.freights_type_ids.type_name).upper()
            if typname == "MULTIMODAL":
                return True
        return False

    def get_default_from(self):
        quotation = self.env["freights.quotations"].browse(self.env.context.get('default_quotation_id'))
        freight = self.env.context.get('default_freight_id')
        print(freight,'===========quotation')
        return quotation.freights_id.origin_point_id.id

    def get_default_dest(self):
        quotation = self.env["freights.quotations"].browse(self.env.context.get('default_quotation_id'))
        return quotation.freights_id.destination_point_id.id
    
    def get_default_validdate(self):
        print("ending_month")
        today = fields.date.today()
        print("ending_month",today)
        ending_month = date_utils.end_of(today, "month")
        print("ending_month",ending_month)
        return ending_month

    sequence = fields.Integer(help="Gives the sequence order when displaying a list of records.", default =0 )

    template_id = fields.Many2one(comodel_name="freights.service.template",)
    agent_id = fields.Many2one(comodel_name="res.partner", string="Agent", help="Захиалга өгсөн менежерийн нэр",domain="[('is_company','=',True)]")
    freights_type_ids = fields.Many2one(comodel_name="freights.type", string="Freight type")
    service_from = fields.Many2one(comodel_name="freights.points", string='From', default = get_default_from)
    service_to = fields.Many2one(comodel_name="freights.points", string='To' , default = get_default_dest)
    quotation_id = fields.Many2one("freights.quotations", string="Quotation", ondelete='cascade') 
    transport_type = fields.Many2one(comodel_name="mlworldwide.transport.type", string='Transport type', )
    fleet=fields.Many2one('delivery.vehicle' , string="Vehicle")
    type = fields.Many2one(comodel_name="freights.service.type", string="Selection", default=1)
    delivery_zone=fields.Many2one('delivery.zone',string="Delivery zone")
    currency_id = fields.Many2one(comodel_name='res.currency', string="Currency", domain=[ ('active', '=', True)], default=lambda self: self.env.company.currency_id)
    rate_currency_id = fields.Many2one(comodel_name='res.currency', string="Rate Currency", domain=[ ('active', '=', True)], default=lambda self: self.env.company.currency_id)
    service_desc = fields.Char(string='Description', ) 
    bill_instruction = fields.Char(string='Bill instruction')
    purpose = fields.Char(string="Purpose")
    cost_message = fields.Char(compute='_compute_cost_message', string=' ', help=' ')

    service_qty = fields.Float(string='Quantity', help="Төсөвлөсөн тоо", default = 1.00)
    service_cost = fields.Float(string='Total', help="MLW үнэ /НӨАТ-гүй үнэ/")
    subtotal_cost = fields.Float(string='Subtotal', help="MLW үнэ /НӨАТ-гүй үнэ/", compute='_compute_cost') 
    have_unit_rate = fields.Boolean(string='I Have unit rate')
    # UNIT RATE
    unit_cost = fields.Float(string='Unit', help="MLW баталсан үнэ /НӨАТ-гүй үнэ/")
    # UNIT qRATE
    unit_qrate = fields.Float(string='Unit QRate', help="MLW баталсан үнэ /НӨАТ-гүй үнэ/")
    total_qrate = fields.Float(string='QRate', help="")
    q_rate_currency_id = fields.Many2one(comodel_name='res.currency', string="Rate Currency", domain=[ ('active', '=', True)], default=lambda self: self.env.company.currency_id)
    # FREIGHT, OTHER CHARGES TOTAL
    service_rate = fields.Float(string='Rate', help="MLW баталсан үнэ /НӨАТ-гүй үнэ/")
    subtotal_rate = fields.Float(string='Subtotal rate', help="MLW баталсан үнэ /НӨАТ-гүй үнэ/", compute='_compute_rate') 
    ett = fields.Integer(string="ETT",help="")

    recipents = fields.Many2many(comodel_name="res.partner", string="Recipents", domain="[('is_company', '=', False)]") 
    
    valid_until_date = fields.Date(string="Valid Until date", help="", default=get_default_validdate)

    remark = fields.Text(string="remark")

    days = fields.Integer(string="days")
    item_qty = fields.Integer()

    at_cost = fields.Boolean(string="At Cost", default=False, help="Show")
    show_qrat_on_pdf = fields.Boolean(string="Show QRate on PDF", default=False, help="Show")
    domestic = fields.Boolean(string="Domestic", default=False, help="Show")
    show_freghts_service = fields.Boolean(default=False, help="Show")
    show_other_service = fields.Boolean(default=False, help="Show")
    show_package_service = fields.Boolean(default=False, help="Show")
    show_thc_service = fields.Boolean(default=False, help="Show")
    show_custiom_service = fields.Boolean(default=False, help="Show")
    show_delivery_service = fields.Boolean(default=False, help="Show")  
    isWeightable = fields.Boolean(default=get_default_isWeightable, help="Show")  
    show_qrate = fields.Boolean(default=get_default_qrate, help="Show")
    isMultimodal = fields.Boolean(default=get_default_modal, help="Show")
    days =fields.Integer(string="Days")
    purpose_radio_domain = fields.Char(compute='_compute_purpose_radio', readonly=True, store= True, )
    purpose_radio = fields.Many2one('service.types', force_save='1')
    
    @api.model
    def get_filtered_purpose_data(self):
        arr = []
        data = self.env['service.types'].search([])
        for rec in data:
            arr.append({
                'id' : rec.id,
                'name' : rec.purpose
            })
        return arr

    @api.onchange('type')
    def _get_default_ubtz(self):
        if self.type.id == 3:
            ubtz = self.env["res.partner"].search([('name', '=', 'UBTZ')], limit=1)
            self.agent_id = ubtz.id

        

    @api.depends('type')
    def _compute_purpose_radio(self):
        for rec in self:
            rec.purpose_radio_domain = json.dumps([('type.name', '=', rec.type.name)])
            rec.purpose = ""
            rec.purpose_radio = False
            # print(rec.purpose_radio_domain,'====================',)

    @api.onchange('freights_type_ids')
    def _onchange_freights_type_ids(self):
        for rec in self:
            if rec.freights_type_ids:
                if rec.freights_type_ids.type_name.lower() == 'air':
                    rec.show_qrate = True
            
    
    @api.onchange('days','purpose','type')
    def _onchange_item_qty(self):
        if self.type.name =='THC':
            thc = self.env["ths.rates"].search([(
                'terminal.name' ,'=', self.quotation_id.freights_id.terminal_id.name
            ),(
                'taras_id.id','=',self.quotation_id.taras_ids.id
            )])
            for rec in thc:
                if rec.service_type == self.purpose:
                    self.service_cost =  rec.cost_data*self.days


    @api.onchange('type', 'purpose', 'item_qty')
    def _onchange_costs(self):
        if self.purpose and self.type.name == 'Customs':
            terminal_rates = self.env['customers.rates'].search([('service_data_eng','=', self.purpose),('point_data.id', '=', self.quotation_id.freights_id.terminal_id.id)])
            for rate in terminal_rates:
                if self.item_qty > rate.from_data and self.item_qty < rate.to_data:
                    self.service_cost = rate.cost_data
                    self.currency_id = rate.currency_id.id

    @api.onchange('purpose_radio')
    def _onchange_purpose_radio(self):
        self.purpose = self.purpose_radio.purpose
        self.auto_fill_cost()
   
    @api.model
    def create(self, values):
        if 'type' in values:
            if values["type"]:
                if values["type"] == 1:
                    values["show_freghts_service"] = True
                elif values["type"] == 2:
                    values["show_other_service"] = True 
                elif values["type"] == 3:
                    values["show_package_service"] = True
                elif values["type"] == 4:
                    values["show_thc_service"] = True
                elif values["type"] == 5:
                    values["show_custiom_service"] = True
                elif values["type"] == 6:
                    values["show_delivery_service"] = True
        if "quotation_id" in values:
            print(values["quotation_id"])

        res = super(FreightsServicesModel, self).create(values)
        print("res",res)
        # if res.quotation_id and (res.type == 1 or res.type == 3):
        #     start = res.quotation_id.freights_id.origin_point_id.id
        #     end = res.quotation_id.destination_point_id.id
        #     shgowmsg = False
        #     for rec in res.quotation_id.service_ids:
        #         if (rec.type == 1 or rec.type == 3) and rec.service_to.id == end:
        #             shgowmsg = True
        #     if not shgowmsg:
        #         res.quotation_id.warning_message = "Insert all freight costs"
        #     else: 
        #         res.quotation_id.warning_message = ""
        # if res.show_qrate:
        #     abroad_rate = 0
        #     for rec in res.quotation_id.service_ids:
        #         abroad_rate += rec.total_qrate
        #     res.quotation_id.abroad_rate = abroad_rate
        #     res.quotation_id.abroad_rate_currency = self.env.company.currency_id

        return res
    
    # @api.model
    # def write(self, values):
    #     if 'type' in values:
    #         if values["type"]:
    #             if values["type"] == 1:
    #                 values["show_freghts_service"] = True
    #             elif values["type"] == 2:
    #                 values["show_other_service"] = True 
    #             elif values["type"] == 3:
    #                 values["show_package_service"] = True
    #             elif values["type"] == 4:
    #                 values["show_thc_service"] = True
    #             elif values["type"] == 5:
    #                 values["show_custiom_service"] = True
    #             elif values["type"] == 6:
    #                 values["show_delivery_service"] = True
    #     if "quotation_id" in values:
    #         print(values["quotation_id"])
    #     res = super(FreightsServicesModel, self).write(values)
    #     print("res",res)
    #     if res.quotation_id and res.type == 1:
    #         print("")
        # if res.show_qrate:
        #     abroad_rate = 0
        #     for rec in res.quotation_id.service_ids:
        #         if rec.total_qrate:
        #             abroad_rate += rec.total_qrate
        #     res.quotation_id.abroad_rate = abroad_rate
        #     res.quotation_id.abroad_rate_currency = self.env.company.currency_id

    @api.onchange("service_from","service_to")
    def _onchange_fromto_service(self):
        self.auto_fill_cost()
     
    # @api.onchange("unit_qrate")
    # def _onchange_unit_qrate(self):
    #     print(self.quotation_id.chargabel_weight, " self.quotation_id.chargabel_weight")


    @api.onchange("unit_cost", "unit_qrate")
    def _onchange_unit_cost(self):
        print(self.quotation_id.chargabel_weight, " self.quotation_id.chargabel_weight")
        if self.have_unit_rate and self.quotation_id.chargabel_weight:
            self.service_cost = self.unit_cost * self.quotation_id.chargabel_weight
        if self.quotation_id.chargabel_weight:
            self.service_rate = self.unit_qrate * self.quotation_id.chargabel_weight
    

    #  cost_message field-g hooslono
    def _compute_cost_message(self):
        for record in self:
            record.cost_message = ""

    def auto_fill_cost(self):
          for record in self:
            if record.type.id == 3:
                self._FOB_FILTER()
            elif record.type.id == 4:
                self._THC_FILTER()
            elif record.type.id == 5:
                self._CUSTOM_FILTER()
            elif record.type.id == 6:
                self._DELIVERY_FILTER()
    
    def _CUSTOM_FILTER(self):
        self.at_cost = True

    def _FOB_FILTER(self):
        for record in self:
            loaded = False
            unloaded = False
            for src in record.quotation_id.service_ids:
                if src.type.id == 3 and src.purpose:
                    if src.purpose.upper() == "LOADED":
                        loaded = True
                    elif src.purpose.upper() == "UNLOADED":
                        unloaded = True
            if record.agent_id:
                child_ids = self.env['res.partner'].search([('parent_id', '=', record.agent_id.id)]) #agent_id field-n id-g awj res.partner-n parent_id field-r tentsvlj haina
                record.recipents = child_ids
                if "ubtz" in record.agent_id.name.lower():
                    ftype = False
                    for ft in record.quotation_id.freights_type_ids:
                        if ft.type_name == "FCL":
                            ftype =True
                    empty = "1"
                    if record.purpose:
                        if record.purpose.upper() == "LOADED":
                            empty = "1"
                        elif record.purpose.upper() == "UNLOADED":
                            empty = "0"
                    # issearch = True
                    # if record.quotation_id.container_type and record.quotation_id.container_type.name.upper() == "COC":
                    #     if not loaded:
                    #         empty = "0"
                    #     if loaded and unloaded:
                    #         issearch = False
                    # else:
                    #     empty = "0"
                    #     if loaded:
                    #         issearch = False
                    if (ftype and record.service_from and record.service_to and record.quotation_id.taras_ids.id and record.quotation_id.freights_id.terminal_id):
                        # fob.rates -r filter-ded service_cost, ett, currency_id field-vded utga ugnu
                        fob = self.env['fob.rates'].search([
                            ('agent_data', '=', record.agent_id.id),
                            ('from_data', '=', record.service_from.id),
                            ('to_data', '=', record.service_to.id),
                            ('empty', '=', empty),
                            ('taras_data', '=', record.quotation_id.taras_ids.taras_type),
                            ('terminal', '=', record.quotation_id.freights_id.terminal_id.id)
                        ], limit=1, order="enddate DESC")
                        record.service_cost=fob.cost_data
                        record.ett=fob.ett
                        record.currency_id=fob.currency_id
                        record.valid_until_date = fob.enddate


                        #   Date between checking
                        record.cost_message = "Auto"
                        today = fields.Datetime.now()
                        if fob.enddate:
                            if fob.enddate < today.date():
                                diff = (fob.enddate - today.date())
                                record.cost_message = _('In %d days ago') % (diff.days, )
                        if fob.startdate:
                            if fob.startdate > today.date():
                                diff = (today.date() - fob.startdate)
                                record.cost_message = _('In %d days later') % (diff.days, ) 
             

    # delivery.rates-r filterded service_cost,currency_id field-vded utga uguud, cost_message-d utga ugnu
    def _DELIVERY_FILTER(self):
        print(" !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        for record in self:
            if record.agent_id and record.quotation_id.freights_id.terminal_id:
                delivery = self.env['delivery.rates'].search([
                    ('agent_id', '=', record.agent_id.id),
                    ('fleet', '=', record.fleet.id),
                    ('terminal', '=', record.quotation_id.freights_id.terminal_id.id),
                ], limit=1, order="end_date DESC")
                record.service_cost=delivery.cost_data
                record.currency_id=delivery.currency_id
                #   Date between checking
                record.cost_message = "Auto"
                today = fields.Datetime.now()
                if delivery.end_date:
                    if delivery.end_date < today.date():
                        diff = (delivery.end_date - today.date())
                        record.cost_message = _('In %d days ago') % (diff.days, )
                if delivery.start_date:
                    if delivery.start_date > today.date():
                        diff = (today.date() - delivery.start_date)
                        record.cost_message = _('In %d days later') % (diff.days, ) 
                

    def _THC_FILTER(self):
        for record in self:
            if record.agent_id:
                ftype = False
                for ft in record.quotation_id.freights_id.freigths_type: #gadnah worldwide.freight-s freights_type field-n utgig awan LCL,LTL, FCL bwal ftype-g true bolgono
                    if ft.type_name == "FCL" or ft.type_name == "LCL" or ft.type_name == "LTL":
                        ftype =True
                if (ftype and record.quotation_id.container_type and record.quotation_id.taras_ids.id and record.quotation_id.freights_id.terminal_id):
                    # ths.rates -s filterded utga ugnu
                    thc = self.env['ths.rates'].search([
                        # ('agent_data', '=', record.agent_id.id),
                        ('container', '=', record.quotation_id.container_type.id),
                        ('taras_id', '=', record.quotation_id.taras_ids.id),
                        ('terminal', '=', record.quotation_id.freights_id.terminal_id.id),
                    ], limit=1, order="end_date DESC")
                    record.service_cost=thc.cost_data*self.item_qty
                    record.currency_id=thc.currency_id
                    #   Date between checking
                    record.cost_message = "Auto"
                    today = fields.Datetime.now()
                    if thc.end_date:
                        if thc.end_date < today.date():
                            diff = (thc.end_date - today.date())
                            record.cost_message = _('In %d days ago') % (diff.days, )
                    if thc.start_date:
                        if thc.start_date > today.date():
                            diff = (today.date() - thc.start_date)
                            record.cost_message = _('In %d days later') % (diff.days, ) 

    @api.onchange("show_thc_service")
    def _onchange_thc_service(self):
        if self.show_thc_service:
            self._THC_FILTER()
    

    # type field uurchlugdwul doorh vildlvdig hiine
    @api.onchange("type")
    def _onchange_service_type(self):
        # print(self.purpose_radio.purpose,'self.type.name=========')
        for record in self:
            record.show_freghts_service = False
            record.show_other_service = False
            record.show_package_service = False
            record.show_thc_service = False
            record.show_custiom_service = False
            record.show_delivery_service = False
            if self.type.id == 1:
                record.show_freghts_service = True
            elif self.type.id == 2:
                record.show_other_service = True 
            elif self.type.id == 3:
                record.show_package_service = True
                if record.quotation_id.freights_type_ids.type_name:
                    name = record.quotation_id.freights_type_ids.type_name.upper()
                    if name == "FCL":
                        ValidationError("Only for FCL")
            elif self.type.id == 4:
                record.show_thc_service = True
            elif self.type.id == 5:
                record.show_custiom_service = True
            elif self.type.id == 6:
                record.show_delivery_service = True

    # service_cost, service_qty hoorondn vrjvvled subtotal_cost-d utga onoono
    def _compute_cost(self):
        for record in self:
            record.subtotal_cost = record.service_cost * record.service_qty

    # service_rate, service_qty hoorondn vrjvvled subtotal_rate-d utga onoo
    @api.depends('service_rate', 'service_qty')
    def _compute_rate(self):
        for record in self:
            record.subtotal_rate = record.service_rate * record.service_qty

    def remove(self):
        print("REEMOVE")

    # wizard gargaj irne
    def show_wizard(self):
        self.ensure_one()
        return {
            'name': "Service",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'freights.service',
            'res_id': self.id,
            'target': 'new',
        }
    # template_id field uurchlugdwul ternes data awan field-vded ugnu
    @api.onchange('template_id')
    def _onchange_template_id(self):
        for rec in self:
            if rec.template_id:
                rec.agent_id = rec.template_id.agent_id
                rec.service_from = rec.template_id.service_from
                rec.service_to = rec.template_id.service_to
                rec.transport_type = rec.template_id.transport_type
                rec.service_desc = rec.template_id.service_desc
                rec.service_qty = rec.template_id.service_qty
                rec.currency_id = rec.template_id.currency_id
                # rec.agent_costs_ids = rec.template_id.agent_costs_ids
                rec.service_cost = rec.template_id.service_cost
                rec.service_rate = rec.template_id.service_rate
                rec.ett = rec.template_id.ett
                rec.valid_until_date = rec.template_id.valid_until_date
                rec._compute_cost()
                rec._compute_rate()

    @api.onchange('agent_id')
    def display_notif(self):
        print(self.agent_id,'==')
        self.auto_fill_cost()
        for inquiry in self.quotation_id.freights_id.freights_inquiries:
            for agent in inquiry.agent_id:
                if agent._origin.id == self.agent_id.id:
                    if len(inquiry.agent_costs_ids) > 0:
                        print(inquiry.agent_costs_ids[0].currency_id.id,'------', self.currency_id.id)
                        self.service_cost = inquiry.agent_costs_ids[0].service_cost
                        self.valid_until_date = inquiry.agent_costs_ids[0].valid_until_date
                        self.currency_id = inquiry.agent_costs_ids[0].currency_id.id
                        self.ett = inquiry.agent_costs_ids[0].ett
                        self.service_from = inquiry.origin_point_id.id
                        self.service_to = inquiry.destination_point_id
                        self.transport_type = inquiry.agent_costs_ids[0].transport_type.id
                        break
        latest_contract = ""
        if self.agent_id:
            self.recipents = self.env['res.partner'].search([('parent_id', '=', self.agent_id.id)]) #agent_id field-n id-g awj res.partner-n parent_id field-r tentsvlj haina
            if self.agent_id.freigths_contracts:
                for contract in self.agent_id.freigths_contracts:
                    if latest_contract == "":
                        latest_contract = contract.contract_expired_date
                    if latest_contract < contract.contract_expired_date:
                        latest_contract = contract.contract_expired_date
            if latest_contract != "":
                if fields.Datetime.from_string(latest_contract).date() < datetime.date.today():
                    print('0---------------lmao-----------')                
                    return {
                        'warning': {
                        'title': _('Warning'),
                        'message': _('Contract Expired')
                        }   
                    }
             
        return {
            'warning':{
                'title': _('Warning'),
                'message' : _('There is no contract')
            }
        }


    # @api.onchange('purpose')
    # def _onchange_service_fromto(self):
    #     print("-----------------------------------------------------")
        
    def name_get(self):
        result = []
        for rec in self:
            str1 = "Unknown"
            if rec.service_from:
                str1 = rec.service_from.name
            str2 = "Unknown"
            if rec.service_to:
                str2 = rec.service_to.name
            str3 = ""    
            if rec.quotation_id:
                str3 = rec.quotation_id.freights_id.ref_num
            result.append((rec.id, '%s / %s - %s' % (str(str3), str(str1), str(str2))))
        return result


class FreightsServicesTemplateModel(models.Model):
    _name = "freights.service.template"
    _description = "Worldwide freights service template model"
    
    # freights.cost.type model-n bvh record-g awan lst array rv nerign pushlene
    def _get_one2many_records(self):        
        lst = []
        one2many_record_obj = self.env['freights.cost.type'].search([])        
        for data in one2many_record_obj:
            lst.append((data.name, data.name))
        return lst
    
    # freights.cost.type model-n bvh record-g awan lst array rv id pushled 0 doh index ig butsana
    def _get_one2many_default(self):        
        lst = []
        one2many_record_obj = self.env['freights.cost.type'].search([])        
        for data in one2many_record_obj:
            lst.append(data.id)
        return lst[0]    
        
    type = fields.Selection(_get_one2many_records, string="Selection", default=_get_one2many_default)
    agent_id = fields.Many2one(comodel_name="res.partner", string="Agent", help="Захиалга өгсөн менежерийн нэр")
    service_from = fields.Char(string='From', )
    service_to = fields.Char(string='To', )
    transport_type = fields.Many2one(comodel_name="mlworldwide.transport.type", string='Transport type', )
    service_desc = fields.Char(string='Description', )
    service_qty = fields.Float(string='Quantity', help="Төсөвлөсөн тоо", default = 1.00)
    currency_id = fields.Many2one(comodel_name='res.currency', string="Currency", domain=[('active', '=', True)], default=lambda self: self.env.company.currency_id)
    service_cost = fields.Float(string='Cost', help="MLW үнэ /НӨАТ-гүй үнэ/", )
    subtotal_cost = fields.Float(string='Subtotal', help="MLW үнэ /НӨАТ-гүй үнэ/",) 
    service_rate = fields.Float(string='Rate', help="MLW баталсан үнэ /НӨАТ-гүй үнэ/", ) 
    subtotal_rate = fields.Float(string='Subtotal rate', help="MLW баталсан үнэ /НӨАТ-гүй үнэ/",) 
    ett = fields.Float(string="ETT",help="")
    valid_until_date = fields.Datetime(string="Valid Until date", help="")
    start_date =fields.Date(string="Start date", help="")
    end_date =fields.Date(string="End date", help="")
    name = fields.Many2one('freights.terminal' ,string="terminal")
    empty = fields.Boolean(string="Empty return")
    taras_id = fields.Many2one('freights.taras', string='Taras')
    delivery_zone=fields.Many2one('delivery.zone',string="Delivery zone")
    fleet=fields.Many2one('delivery.vehicle' , string="vehicle")
    quotation_id = fields.Many2one("freights.quotations", string="Quotation")

    @api.onchange("type")
    def _change_type(self):
        print(self.type)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, '%s - %s' % (str(rec.service_from), str(rec.service_to))))
        return result
