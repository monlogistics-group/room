# -*- coding: utf-8 -*-
# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2023-03-27

from odoo import api, fields, models, _

class AddEmployeeRole(models.Model):
    _inherit = "hr.employee"

    @api.model
    def create(self, values):
        result =  super(AddEmployeeRole, self).create(values)
        self.env['freights.employee.role'].create({
            'employee' : result.id
        })
        return result


        