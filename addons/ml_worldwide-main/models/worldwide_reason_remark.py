# -*- coding: utf-8 -*-
# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-12-02

from random import randint
from odoo import fields, models

class WorldwideReasonRemark(models.Model):
    _name = "mlworldwide.reason.remark"
    _description="Worldwide create reason remark"

    def _get_default_color(self):
        return randint(1, 11)
    
    reason_remark_type=fields.Many2one(comodel_name="mlworldwide.reason", string='Type')
    base_id= fields.Char()
    note=fields.Char(string="Note")
    
    def cancel_button(self):
        freights = self.env["mlworldwide.freights"].search([('id', '=' ,self.base_id)],limit =1)
        freights.state_id = 'cancelled'
        activated = freights.filtered(lambda WorldwideReasonRemark:  WorldwideReasonRemark.cancel_active)
        if activated:
            activated.write({'cancel_active': False})
            freights.lost_reason = self.reason_remark_type
            freights.note = self.note