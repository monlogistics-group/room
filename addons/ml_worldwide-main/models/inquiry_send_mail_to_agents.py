# -*- coding: utf-8 -*-
# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2022-12-23

from odoo import models, fields

class InquirySendMailToAgents(models.TransientModel):
    _inherit = "mail.compose.message"

    def action_send_mail(self):
        inquiry = self.env.context.get('default_res_id')
        model = self.env.context.get('default_model')
        if model == 'freights.agent.inquiry':
            get_model = self.env['freights.agent.inquiry'].search([('id','=',inquiry)],limit=1)
            template_rec = self.env.ref('ml_worldwide-main.mail_template_data_agent_inquiry')
            for rec in get_model.agent_id:
                arr = []
                for child in rec.child_ids:
                    arr.append(child.email)
                mails=','.join([str(elem) for elem in arr])
                template_rec.sudo().write({
                    'email_to' : mails
                })
                self.partner_ids = rec.child_ids
                if mails:
                    template_rec.send_mail(inquiry, force_send=True)
                    get_model.agent_costs_ids += self.env['freights.agent.cost'].create({
                        'agent_id' : rec.id
                    })
                    get_model.checker = True
        elif model == 'freights.quotations':
            get_model = self.env['freights.quotations'].search([('id','=',inquiry)],limit=1)
            get_model.state_id = 'sent'
        super(InquirySendMailToAgents,self).action_send_mail()

