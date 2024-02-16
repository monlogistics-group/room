# -*- coding: utf-8 -*-
# Created by Umbaa. 2023-06-05

from odoo import fields, models
from datetime import datetime, timedelta

class InsuranceAppindex(models.TransientModel):
    _name = 'insurance.appendix'
    _description = "Insurance appendix"

    def _get_default_pls_start_date(self):
        return datetime.now() - timedelta(days=14)
    
    def _get_default_pls_end_date(self):
        return datetime.now()

    start_date = fields.Date(required=True, default=_get_default_pls_start_date)
    end_date = fields.Date(required=True, default=_get_default_pls_end_date)

    def action_insurance_appendix(self):
        # allFreights = self.env['mlworldwide.freights'].search([('freights_routes_shipment.atd_date', '>', self.start_date), ('freights_routes_shipment.atd_date', '<', self.end_date)])
        data = {}
        date_from = fields.Datetime.from_string(self.start_date)
        date_to = fields.Datetime.from_string(self.end_date)
        data["from_date"] = date_from
        data["to_date"] = date_to

        return self.env.ref(
            "ml_worldwide-main.action_insurance_appendix_report"
        ).report_action(self, data=data)

    def export_insurance_cases(self):
        data = {}
        date_from = fields.Datetime.from_string(self.start_date)
        date_to = fields.Datetime.from_string(self.end_date)
        data["from_date"] = date_from
        data["to_date"] = date_to

        return self.env.ref(
            "ml_worldwide-main.action_insurance_cases_report"
        ).report_action(self, data=data)
    
    def register_insurance_cases(self, shipment_id):
        data = {}
        data["shipment_id"] = shipment_id
        return self.env.ref(
            "ml_worldwide-main.action_insurance_register"
        ).report_action(self, data=data)