# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2023-04-03
import base64

from email.policy import default
from odoo import api, fields, models
class PreviewPdfWizard(models.TransientModel):
    _name = 'preview.pdf.wizard'
    
    freights_package = fields.Many2one('freights.packages')
    preview_pdf = fields.Binary(compute='_computed_preview_pdf')
    
    def _computed_preview_pdf(self):
        report = self.env['ir.actions.report']._get_report_from_name('ml_worldwide-main.cargo_receipt')
        report_data = report._render_qweb_pdf(self.id)[0]
        self.preview_pdf = base64.b64encode(report_data)

    def cancel(self):
        print('-')