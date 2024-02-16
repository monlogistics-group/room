# -*- coding: utf-8 -*-
# Copyright 2023 Mon Logistics Group <https://www.mlholding.mn>


from odoo import models, fields
from datetime import datetime

class MonthlyReport(models.Model):
    _name = "monthly.report"
    
    def _get_employee_id(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        return employee_rec.id
    
    reportDate = fields.Datetime(string='Created', default=datetime.now(), readonly=True)
    reportmonth = fields.Date( string='Month')
    subject = fields.Char()
    base_id= fields.Char()

    freight_id=fields.Many2many(comodel_name="mlworldwide.freights" , string="Freight transient")
    
    employee = fields.Many2one('hr.employee', string="Creater", default=_get_employee_id, readonly=True, required=True, help="Захиалга өгсөн менежерийн нэр")
    customer_id = fields.Many2one('res.partner' , 'Partner')
    
    # Unfortunetly function
    def zzzz(self):
        report = self.env['ir.actions.report']._get_report_from_name('ml_worldwide-main.monthly_report')
        report.report_type = 'qweb-html'
        html = report.report_action(self, config = False)
        return html
        
    """ Montly report action """
    def action_send(self):
        self.ensure_one()
        template_id = self.env.ref('ml_worldwide-main.mlworldwide_monthly_report_template').id
        ctx = {
            'default_model': 'monthly.report',
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }  

    