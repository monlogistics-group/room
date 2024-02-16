# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2023-04-03
import base64

from email.policy import default
from odoo import api, fields, models
class SearchWizard(models.TransientModel):
    _name = 'package.wizard'
    
    late_reason = fields.Char()
    helper_id = fields.Integer()
    
  
    def package_wizard(self):
        package = self.env['freights.packages'].search([('id', '=', self.helper_id)], limit=1)
        package.note = self.late_reason
        print('--------')
    