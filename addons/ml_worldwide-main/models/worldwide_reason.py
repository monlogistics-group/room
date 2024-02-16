# -*- coding: utf-8 -*-
# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-12-02

from random import randint
from odoo import fields, models

class WorldwideReason(models.Model):
    _name = "mlworldwide.reason"
    _order = 'sequence asc'
    _rec_name = "name"
    _description="Worldwide create reason"

    def _get_default_color(self):
        return randint(1, 11)
    
    color = fields.Integer(string='Color', default=_get_default_color)
    name = fields.Char(required=True, translate=True)
    
    sequence = fields.Integer(help="Used to order the note stages")
    def _compute_leads_count(self):
        lead_data = self.env['worldwide.freights'].with_context(active_test=False).read_group([('lost_reason', 'in', self.ids)], ['lost_reason'], ['lost_reason'])
        mapped_data = dict((data['lost_reason'][0], data['lost_reason_count']) for data in lead_data)
        for reason in self:
            reason.leads_count = mapped_data.get(reason.id, 0)



