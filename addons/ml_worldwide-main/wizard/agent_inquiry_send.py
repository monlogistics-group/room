# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons.mail.wizard.mail_compose_message import _reopen
from odoo.exceptions import UserError
from odoo.tools.misc import get_lang


class AgentInquirySend(models.TransientModel):
    _name = 'agent.inquiry.send'
    _inherits = {'mail.compose.message':'composer_id'}
    _description = 'Agent Inquiry Send'

    def _get_default_mail_to_ids(self):
        res_ids = self._context.get('active_ids')
        inquiries = self.env["freights.agent.inquiry"].browse(res_ids)
        # agents = self.env["inquiry.mail.to"].sudo().create({
        #         'agent_id': inquiries.agent_id[0]
        #     })
        # i = 0
        # for agent in inquiries.agent_id:
        #     if i != 0:
        #         agent_ids = self.env["inquiry.mail.to"].sudo().create({
        #             'agent_id': agent.id
        #         })
        #         agents += agent_ids
        #     i += 1
        # return agents

    composer_id = fields.Many2one('mail.compose.message', string='Composer', required=True, ondelete='cascade')
    template_id = fields.Many2one(
        'mail.template', 'Use template', index=True,
        domain="[('model', '=', 'account.move')]"
        )
    # inquiry_mail_to_ids = fields.Many2many('inquiry.mail.to', string='To', required=True, ondelete='cascade', default=_get_default_mail_to_ids)
    # inquiry_mail_to_ids = fields.Many2many('inquiry.mail.to', string='To', required=True, ondelete='cascade')
    @api.model
    def default_get(self, fields):
        res = super(AgentInquirySend, self).default_get(fields)
        self.composition_mode = "comment"
        composer = self.env['mail.compose.message'].create({
            'composition_mode': 'comment'
        })
        res.update({
            'composer_id': composer.id,
        })
        return res

    @api.onchange('template_id')
    def onchange_template_id(self):
        for wizard in self:
            if wizard.composer_id:
                wizard.composer_id.template_id = wizard.template_id.id
                # wizard._compute_composition_mode()
                wizard.composer_id._onchange_template_id_wrapper()

    def _send_email(self):
        res_ids = self._context.get('active_ids')
        inquiries = self.env["freights.agent.inquiry"].browse(res_ids)
        self.composition_mode = "comment"
        for agent in inquiries.agent_id:
            for contact in agent.child_ids:
                self.partner_ids = [(4, contact.id, contact)]
            # send email to agents employer
            self.composer_id.with_context(mail_notify_author=self.env.user.partner_id in self.composer_id.partner_ids,
                                            mailing_document_based=True
                                            )._action_send_mail()
            for contact in agent.child_ids:
                self.partner_ids = [(3, contact.id, contact)]

            agent_cost = self.env["freights.agent.cost"].sudo().create({
                'agent_id': agent.id
            })
            inquiries.agent_costs_ids += agent_cost

       
    def send_and_print_action(self):
        self.ensure_one()

        if self.composition_mode == 'mass_mail' and self.template_id:
            active_ids = self.env.context.get('active_ids', self.res_id)
            active_records = self.env[self.model].browse(active_ids)
            langs = active_records.mapped('partner_id.lang')
            default_lang = get_lang(self.env)
            for lang in (set(langs) or [default_lang]):
                active_ids_lang = active_records.filtered(lambda r: r.partner_id.lang == lang).ids
                self_lang = self.with_context(active_ids=active_ids_lang, lang=lang)
                self_lang.onchange_template_id()
                self_lang._send_email()
        else:
            self._send_email()
        # if self.is_print:
        #     return self._print_document()
        return {'type': 'ir.actions.act_window_close'}

    def save_as_template(self):
        self.ensure_one()
        self.composer_id.action_save_as_template()
        self.template_id = self.composer_id.template_id.id
        action = _reopen(self, self.id, self.model, context=self._context)
        action.update({'name': _('Send Invoice')})
        return action



