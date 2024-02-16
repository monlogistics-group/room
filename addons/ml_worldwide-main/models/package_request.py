# -*- coding: utf-8 -*-
# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2023-01-24

from odoo import models, fields

class PackageRequest(models.Model):
    _name = "package.request"
    
    name = fields.Char(string='Name')
    requested_date = fields.Date(string='Requested Date')
    where = fields.Char(string='Where')
    field_name = fields.Char(string='Field name')
    package_id = fields.Char()

    state_id = fields.Selection(selection=[
            ('request', 'Request'),
            ('confirmed', 'Confirmed'),
        ], default='request')

    # Package state Confirm
    def confirm(self):
        if self.field_name == 'Customs date start':
            package = self.env['freights.packages'].search([('id', '=', self.package_id)],limit=1)
            package.customs_date_start_boolean = False
        elif self.field_name == 'Customs date end':
            package = self.env['freights.packages'].search([('id', '=', self.package_id)],limit=1)
            package.customs_date_end_boolean = False
        elif self.field_name == 'Assessment date start':
            package = self.env['freights.packages'].search([('id', '=', self.package_id)],limit=1)
            package.assessment_date_start_boolean = False
        elif self.field_name == 'Assessment date end':
            package = self.env['freights.packages'].search([('id', '=', self.package_id)],limit=1)
            package.assessment_date_end_boolean = False
        self.state_id= 'confirmed'