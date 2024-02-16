
from odoo import api, fields, models

class InquiryData(models.Model):
    _name = "inquiry.data"
    _description = "Freight inquiry data model"
    
    def _lang_get(self):
        langs = self.env['res.lang'].get_installed()
        return langs
    
    text_l1=fields.Char(string=" tex_l1")
    text_l2=fields.Char(string=" tex_l2")
    text_l3=fields.Char(string=" tex_l3")
    text_l4=fields.Char(string=" tex_l4")
    text_l5=fields.Char(string=" tex_l5")
    # lang = fields.Many2one(string="Language",comodel_name='res.lang', domain=['|', ('active', '=', False), ('active', '=', True)])
    locale = fields.Many2one(string="Language",comodel_name='res.lang', domain=['|', ('active', '=', False), ('active', '=', True)])
    customer_id = fields.Many2one(comodel_name="res.partner", string="Customer", help="Захиалагч")
    def action_send_all(self):
        self.ensure_one()
        base_id=self.env.context.get('default_freight_id')
        base_freight = self.env['mlworldwide.freights'].search([('id', '=', base_id)])
        base_freight.ctx = self.id
        self.ensure_one()
        template = self.env.ref('ml_worldwide-main.email_all_template_name')
        
        for rec in self.customer_id:
            arr = []
            for child in rec.child_ids:
                arr.append(child.email)
            mails=','.join([str(elem) for elem in arr])
            template.write({
                'email_to' : mails
            })
           
        print(self.id,'----------------------')
        print(base_id,'----------------------')
        ctx = {
            'default_model': 'mlworldwide.freights',
            'default_res_id': base_id,
            'default_use_template': bool(template.id),
            'default_template_id': template.id,
          
            'default_composition_mode': 'comment',
            
            
            # 'mark_agent_mail_sent': False,
            # 'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
            # 'model_description': self.with_context(lang=lang).ref,
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

    