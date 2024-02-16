# -*- coding: utf-8 -*-
# Copyright 2022 Cubicsoft LLC.
#   Gerelttsog.Ts <gerelttsog@cubicsoft.mn>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _

class WorldwideContracts(models.Model):
    _name = "worldwide.contract"
    _description = "Contract"

    contract_number = fields.Char('Contract num')
    contract_expired_date = fields.Date('Expire date')
    contract_file = fields.Many2many(comodel_name='ir.attachment', string='Contract file')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    agent = fields.Boolean('Agent')
    cyrillic_name = fields.Char('Cyrillic name')
    trusted = fields.Boolean('Trusted')
    not_billable = fields.Boolean('Not Bill')
    dont_send_sc = fields.Boolean('Don\'t send SC')
    agent_rating = fields.Float('Agent Rating')
    credit_day =  fields.Integer('Credit day')
    interest_percentage = fields.Float('Interest Rate', compute='_compute_interest_percentage')
    erp_code = fields.Char('Erp code')
    bill_instruction = fields.Text(string='Bill Instruction')

    freigths_type = fields.Many2many(comodel_name="freights.type", string="Type", help="Freights type",) 
    freigths_abilities = fields.Many2many(comodel_name="freights.ability", string="Ability", help="Freights Abilities",) 
    freigths_contracts = fields.Many2many(comodel_name="worldwide.contract", string="Contracts", help="Contracts",) 
    
    freights_agent_review = fields.One2many("freights.agent.review", "agent_id", readonly=True,)

    cron_jobs = fields.Many2one(comodel_name="mlworldwide.cron.job", string="Cron jobs", help="Cron jobs",) 

    def _compute_interest_percentage(self):
        for record in self:
            q = 0
            if record.freights_agent_review:
                for review in record.freights_agent_review:
                    q += int(review.rate)           
                record.interest_percentage = q / len(record.freights_agent_review)
            else:
                record.interest_percentage = 0
    
    def action_get_quotation(self):
        self.ensure_one()
        print("action_get_quotation")
        print(self.id)
        print(self._origin.id)
        parent_id = self.env.context.get('default_freight_id') 
        parent_model = self.env.context.get('parent_model') 
        print(parent_id)
        print(parent_model)

    def update_filtered_items(self):
        parent_id = self.env.context['parent_id']
        base = self.env['freights.agent.inquiry'].search([('id','=', parent_id)])
        for rec in self.ids:
            each_agent = self.env['res.partner'].search([('id','=', rec)])
            base.agent_id += each_agent

    def add_filtered_items(self):
        parent_id = self.env.context['parent_id']
        freights = self.env['mlworldwide.freights'].search([('id' , '=', parent_id)])
        created_agent_inquiry = self.env['freights.agent.inquiry'].create({
            'remark' : 'LCL',
            'origin_point_id' : freights.origin_point_id.id,
            'destination_point_id' : freights.destination_point_id.id,
            'freigths_type' : freights.ordered_freights_type.id
        })
        for rec in self.ids:
            filtered_res_partner = self.env['res.partner'].search([('id','=', rec)])
            created_agent_inquiry.agent_id += filtered_res_partner
            
        freights.freights_inquiries += created_agent_inquiry
