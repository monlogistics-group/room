# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-10-27

from email.policy import default
from odoo import api, fields, models

class TruckingServicesModel(models.Model):
    _name = "mltrucking.service"
    _description = "ML Trucking service model"
    _rec_name = 'service_name'
    _order = 'service_name'
        
    template_id = fields.Many2one('mltrucking.service.templates', string="Template")

    service_name = fields.Char('Name', index=True, required=True)
    agent_id = fields.Many2one(comodel_name="res.partner", string="Agent", help="Захиалга өгсөн менежерийн нэр")
    service_id = fields.Many2one(comodel_name="product.product", string="Service", help="Service нэр", domain=[('detailed_type', '=', 'service')])
    service_desc = fields.Char(string='Description', ) #compute='_compute_name',
    cost_currency_id = fields.Many2one(comodel_name='mltrucking.currency', string="Cost currency", default=lambda self: self.env['mltrucking.currency'].search([("currency_name","=","MNT")], limit=1))
    rate_currency_id = fields.Many2one(comodel_name='mltrucking.currency', string="Rate currency", default=lambda self: self.env['mltrucking.currency'].search([("currency_name","=","MNT")], limit=1)) 
    service_qty = fields.Float(string='Quantity', help="Төсөвлөсөн тоо", default = 1.00)
    service_cost = fields.Float(string='Cost', help="MLT Төсөвлөсөн үнэ /НӨАТ-гүй үнэ/", ) #compute='_compute_cost',
    service_rate = fields.Float(string='Rate', help="MLT Төсөвлөсөн үнэ", ) 
    subtotal_cost = fields.Float(string='Subtotal', help="MLTr баталсан үнэ /НӨАТ-гүй үнэ/", compute='_compute_cost') #compute='_compute_sale',
    is_show_quote = fields.Boolean(string="Is show quotation", default=False)
    is_localtrucking = fields.Boolean(string="International truck", default=False)

    def calc_color(self):
        self.color=2

    def _compute_cost(self):
        for record in self:
            record.subtotal_cost = record.service_id.list_price * record.service_qty

    @api.onchange('template_id')
    def _onchange_template_id(self):
        for rec in self:
            if rec.template_id:
                rec.service_name = rec.template_id.service_name
                rec.agent_id = rec.template_id.agent_id
                rec.service_id = rec.template_id.service_id
                rec.service_desc = rec.template_id.service_desc
                rec.cost_currency_id = rec.template_id.cost_currency_id
                rec.rate_currency_id = rec.template_id.rate_currency_id
                rec.service_qty = rec.template_id.service_qty
                rec.service_cost = rec.template_id.service_cost
                rec.service_rate = rec.template_id.service_rate
                rec.is_show_quote = rec.template_id.is_show_quote
                rec.is_localtrucking = rec.template_id.is_localtrucking

class TruckingBudgetServicesModel(models.Model):
    _name = "mltrucking.budget"
    _inherit = "mltrucking.service"
    _description = "ML Trucking budget model"
    
    service_sale = fields.Float(string='Rate', help="MLTr баталсан үнэ /НӨАТ-гүй үнэ/", ) #compute='_compute_sale',
    service_photos=fields.Many2many(comodel_name='mltrucking.freight.photo',)
    service_image=fields.Image( string="Photos")
    service_agent=fields.Char()
    shipment=fields.Char()
    total=fields.Integer(readonly=True)

    state = fields.Selection([
        ('new', 'New'),
        ('confirmed', 'Confirm'),
        ('cancelled', 'Cancelled'),
        ('done', 'Done')
        ], string='Service state', readonly=True, tracking=True)
        
    @api.onchange('template_id')
    def _onchange_template_id(self):
        for rec in self:
            if rec.template_id:
                rec.service_name = rec.template_id.service_name
                rec.agent_id = rec.template_id.agent_id
                rec.service_id = rec.template_id.service_id
                rec.service_desc = rec.template_id.service_desc
                rec.cost_currency_id = rec.template_id.cost_currency_id
                rec.rate_currency_id = rec.template_id.rate_currency_id
                rec.service_qty = rec.template_id.service_qty
                rec.service_cost = rec.template_id.service_cost
                rec.service_sale = rec.template_id.service_sale

    
    @api.onchange('service_id')
    def _onchange_service_id(self):
        for rec in self:
            rec.service_cost = rec.service_id.list_price

    def add_photos(self):
        wizard = self.env['test.model'].create({
            'parent_id' : self.id
        })
        return {
            'name': 'Test Wizard',
            'type': 'ir.actions.act_window',
            'res_model': 'test.model',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new'
        }

    def cancel_state(self):
        self.state='cancelled'
        
    def confirm_state(self):
        self.state='confirmed'
        
class TruckingServiceTemplateModel(models.Model):
    _name = "mltrucking.service.templates"
    _description = "ML Trucking service templates model"
    _rec_name = 'service_name'
    _order = 'service_name'

    service_name = fields.Char('Name', index=True, required=True)
    agent_id = fields.Many2one(comodel_name="res.partner", string="Agent", help="Захиалга өгсөн менежерийн нэр")
    service_id = fields.Many2one(comodel_name="product.product", string="Service", help="Service нэр", domain=[('detailed_type', '=', 'service')])
    service_desc = fields.Char(string='Description', ) #compute='_compute_name',
    cost_currency_id = fields.Many2one(comodel_name='mltrucking.currency', string="Cost currency", default=lambda self: self.env['mltrucking.currency'].search([("currency_name","=","MNT")], limit=1) )
    rate_currency_id = fields.Many2one(comodel_name='mltrucking.currency', string="Rate currency", default=lambda self: self.env['mltrucking.currency'].search([("currency_name","=","MNT")], limit=1) )
    service_qty = fields.Float(string='Quantity', help="Төсөвлөсөн тоо", default = 1.00)
    service_cost = fields.Float(string='Cost', help="MLT Төсөвлөсөн үнэ /НӨАТ-гүй үнэ/", ) #compute='_compute_cost',
    service_rate = fields.Float(string='Rate', help="MLT Төсөвлөсөн үнэ", ) 
    subtotal_cost = fields.Float(string='Subtotal', help="MLTr баталсан үнэ /НӨАТ-гүй үнэ/", compute='_compute_cost') #compute='_compute_sale',
    is_show_quote = fields.Boolean(string="Is show quotation", default=False)
    is_localtrucking = fields.Boolean(string="International truck", default=False)
