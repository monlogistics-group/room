# -*- coding: utf-8 -*-
# Copyright 2023 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2023-01-02

from odoo import models, fields

class CrmLead(models.Model):
    _inherit = "crm.lead"

    def action_create_freights(self):
        ctx = {
            'default_customer_id': self.partner_id.id,
        }
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mlworldwide.freights',
            'view_mode': 'form',
            'context': ctx,
        }