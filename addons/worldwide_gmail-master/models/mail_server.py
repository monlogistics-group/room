# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
import logging
from collections import defaultdict
from odoo import tools
from odoo.exceptions import UserError, ValidationError
import re


_logger = logging.getLogger(__name__)

class MLmailmail(models.Model):
    _inherit = "mail.mail"

    def send(self, auto_commit=False, raise_exception=False):

        # TODO USer iin zuv emailiig olj "tuvshinbayar@mlholding.mn" iin orond damjiilakh ene email oldojhgui bol nemj tohiruukl gej aldaanii medeelel butsaadag bolgoh
        print(self)
        # if len(self) > 1:

        # from_email = self.email_from
        # if from_email == "":
        #     from_email = self.recipients_ids[0].email

        from_email = ""
        
        current_user= self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)

        if from_email == "" or not from_email:
            from_email = current_user.work_email
        else:
            match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', from_email)
            from_email = match.group(0)

        tmp = self.env['ir.mail_server'].search([('smtp_user','=',from_email)])

        if len(tmp)==0:
            return 
            # raise ValidationError("You should go to your profile then check your work email. If it's correct, you should click on test connection button!")
        print('---------------+--------------')
        for mail_server_id, smtp_from, batch_ids in self._split_by_mail_configuration_extend(self.email_from):
            
            smtp_session = None
            try:
                smtp_session = self.env['ir.mail_server'].connect(mail_server_id=mail_server_id, smtp_from=smtp_from)
            except Exception as exc:
                if raise_exception:
                    # To be consistent and backward compatible with mail_mail.send() raised
                    # exceptions, it is encapsulated into an Odoo MailDeliveryException
                    raise MailDeliveryException(_('Unable to connect to SMTP Server'), exc)
                else:
                    batch = self.browse(batch_ids)
                    batch.write({'state': 'exception', 'failure_reason': exc})
                    batch._postprocess_sent_message(success_pids=[], failure_type="mail_smtp")
            else:
                self.browse(batch_ids)._send(
                    auto_commit=auto_commit,
                    raise_exception=raise_exception,
                    smtp_session=smtp_session)
                _logger.info(
                    'Sent batch %s emails via mail server ID #%s',
                    len(batch_ids), mail_server_id)
            finally:
                if smtp_session:
                    smtp_session.quit()
        return super(MLmailmail, self).send(auto_commit,raise_exception)

    def _split_by_mail_configuration_extend(self, email = False):
        """Group the <mail.mail> based on their "email_from" and their "mail_server_id".

        The <mail.mail> will have the "same sending configuration" if they have the same
        mail server or the same mail from. For performance purpose, we can use an SMTP
        session in batch and therefore we need to group them by the parameter that will
        influence the mail server used.

        The same "sending configuration" may repeat in order to limit batch size
        according to the `mail.session.batch.size` system parameter.

        Return iterators over
            mail_server_id, email_from, Records<mail.mail>.ids
        """
        mail_values = self.read(['id', 'email_from', 'mail_server_id'])

        # First group the <mail.mail> per mail_server_id and per email_from
        group_per_email_from = defaultdict(list)
        for values in mail_values:
            mail_server_id = values['mail_server_id'][0] if values['mail_server_id'] else False
            group_per_email_from[(mail_server_id, values['email_from'])].append(values['id'])

        # Then find the mail server for each email_from and group the <mail.mail>
        # per mail_server_id and smtp_from
        mail_servers = self.env['ir.mail_server'].sudo().search([('smtp_user','=',email)], order='sequence')
        group_per_smtp_from = defaultdict(list)
        for (mail_server_id, email_from), mail_ids in group_per_email_from.items():
            if not mail_server_id:
                mail_server, smtp_from = self.env['ir.mail_server']._find_mail_server(email_from, mail_servers)
                mail_server_id = mail_server.id if mail_server else False
            else:
                smtp_from = email_from

            group_per_smtp_from[(mail_server_id, smtp_from)].extend(mail_ids)

        sys_params = self.env['ir.config_parameter'].sudo(True)
        batch_size = int(sys_params.get_param('mail.session.batch.size', 1000))

        for (mail_server_id, smtp_from), record_ids in group_per_smtp_from.items():
            for batch_ids in tools.split_every(batch_size, record_ids):
                yield mail_server_id, smtp_from, batch_ids