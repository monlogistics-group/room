# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError

class Worldwide_gmail(models.Model):
    _inherit = "res.users"

    
    def new_test(self, current_user):
        res = True
        try:
            current_user.sudo().test_smtp_connection()
        except:
            res = False
        return res
    
    mail_pass = fields.Char(string='Password')
    color_bool = fields.Boolean(default=False)
    
    def confirm_mail_pass(self):
        mails = self.env['ir.mail_server'].sudo().search([])
        check = False
        for mail in mails:
            if self.work_email == mail.smtp_user:
                check = True
        if not check:
            name = self.work_email.split('@')[0]
            created_mail = self.env['ir.mail_server'].sudo().create({
                    'name' : name,
                    'smtp_host' : 'smtp.gmail.com',
                    'smtp_port' : '465',
                    'smtp_encryption' : 'ssl',
                    'smtp_user' : self.work_email,
                    'smtp_pass' : self.mail_pass
                })
            b = self.new_test(created_mail)
            if b == False:
                self.sudo().color_bool = False
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                    'title': _('Warning'),
                    'message': 'You cannot do this action now',
                    'sticky': True,
                    }
                }
            else:
                self.sudo().color_bool = True

        else:
            current_user = self.env['ir.mail_server'].sudo().search([('smtp_user','=',self.work_email)],limit=1)
            current_user.sudo().write({
                'smtp_pass' : self.mail_pass
            })
            b = self.new_test(current_user)
            if b == False:
                self.sudo().color_bool = False
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                    'title': _('Warning'),
                    'message': 'You cannot do this action now',
                    'sticky': True,
                    }
                }
            else:
                self.sudo().color_bool = True

        
    