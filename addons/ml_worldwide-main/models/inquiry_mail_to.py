# -*- coding: utf-8 -*-
# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-12-02
from odoo import api, fields, models, _

class InquiryMailTo(models.Model):
    _name = "inquiry.mail.to"
    _description = ''

    agent_id = fields.Many2one(comodel_name="res.partner", string="Agent", help="Захиалга өгсөн менежерийн нэр",domain=[('is_company','=',True)]) 
    child_ids = fields.Many2many(comodel_name="res.partner", string="Emails", readonly=False, store=True)

    @api.onchange('agent_id')
    def _onchange_fagent_id(self):
        for contact in self.agent_id.child_ids:
            self.child_ids = [(4, contact.id, contact)]

