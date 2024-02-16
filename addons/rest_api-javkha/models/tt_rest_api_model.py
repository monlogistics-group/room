# -*- coding: utf-8 -*-

import json
from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from uuid import uuid4
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT as df
from ..controllers.tt_routes import *
from ..controllers.tt_controllers import TORTECS_API_ENDPOINT, TORTECS_API_ENDPOINT_V1


class TortecsRestAPIModel(models.Model):
    _name = 'tortecs.rest.api'
    _description = 'Tortecs Rest API'
    _rec_name = 'tt_name'

    tt_name = fields.Char('Name', required=True)
    tt_api_token = fields.Char('API Token')
    tt_refresh_token = fields.Char('Refresh Token')
    tt_edit_flag = fields.Boolean('Edit', default=False)
    tt_change_validity = fields.Boolean('Want to change validity')
    tt_access = fields.Selection([('all_access', "Full Access"), ('specific', 'Specific Access')],
                                 default='all_access', string="Access")
    tt_validity = fields.Selection([('day', 'Day'), ('month', 'Month'), ('year', 'Year'), ('never', 'Never Expire')],
                                   default='day', string='Validity')
    tt_number = fields.Integer('Enter the number of Expiry')
    tt_model_access = fields.One2many("tortecs.rest.api.rule", 'tt_rest_api_id')
    tt_user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    tt_priority = fields.Integer('Priority', default='1000')
    tt_is_expired = fields.Boolean('Is Expired')
    tt_route = fields.Text('Routes')
    tt_created_date = fields.Datetime('API Token Created On', default=lambda self: fields.Datetime.now(), readonly=True)
    tt_refresh_created_date = fields.Datetime('Created On', default=lambda self: fields.Datetime.now(), readonly=True)
    tt_expired_date = fields.Datetime('API Token Expired On', default=lambda self: self.tt_generate_expire_date())
    tt_refresh_expired_date = fields.Datetime('Expired On', default=lambda self: self.tt_generate_expire_date())

    def write(self, vals):
        if vals.get('tt_api_token'):
            current_date = datetime.now()
            vals.update({
                'tt_is_expired': False,
                'tt_created_date': current_date,
                'tt_refresh_created_date': current_date
            })
            result = self.tt_generate_expire_date(current_date, current_date)
            vals.update(result)
        return super(TortecsRestAPIModel, self).write(vals)

    @api.model
    def create(self, vals):
        vals.update({
            'tt_route': json.dumps(self.tt_generate_route_data())
        })
        rec = super(TortecsRestAPIModel, self).create(vals)
        if not vals.get('tt_api_token'):
            rec.tt_generate_api_key()
        return rec

    def tt_generate_route_data(self):
        tortecs_prefix = TORTECS_API_ENDPOINT + TORTECS_API_ENDPOINT_V1
        route_data = {
            'Authentication': '%s' % tortecs_prefix + tt_auth,
            'Multi Record Creation': '%s/{model}' % tortecs_prefix,
            'Single Record Creation': '%s/{model}/{id}' % tortecs_prefix,
            'Get Multi Record': '%s/{model}' % tortecs_prefix,
            'Get Single Record': '%s/{model}/{id}' % tortecs_prefix,
            'Update Single Record': '%s/{model}/{id}' % tortecs_prefix,
            'Update Multiple Record': '%s/{model}' % tortecs_prefix,
            'Delete Single Record': '%s/{model}/{id}' % tortecs_prefix,
            'Delete Multiple Records': '%s/{model}' % tortecs_prefix,
            'Execute Model Function': '%s/object/{model}/{function}' % tortecs_prefix,
            'Execute Object Function': '%s/object/{model}/{id}/{function}' % tortecs_prefix,
        }
        return route_data

    @api.onchange('tt_created_date', 'tt_number', 'tt_change_validity')
    def tt_generate_expire_date(self, api_date=None, refresh_date=None):
        if api_date is None and refresh_date is None:
            api_create_date = self.tt_created_date
            refresh_create_date = self.tt_refresh_created_date
        else:
            if isinstance(api_date, datetime) and isinstance(refresh_date, datetime):
                api_create_date = api_date
                refresh_create_date = refresh_date
            else:
                api_create_date = datetime.strptime(api_date, df)
                refresh_create_date = datetime.strptime(refresh_date, df)

        if self.tt_change_validity and self.tt_number != 0:
            if self.tt_validity == 'day':
                api_expired_date = api_create_date + timedelta(days=self.tt_number)
                refresh_expired_date = refresh_create_date + timedelta(days=self.tt_number)
            elif self.tt_validity == 'month':
                api_expired_date = api_create_date + relativedelta(months=self.tt_number)
                refresh_expired_date = refresh_create_date + relativedelta(months=self.tt_number)
            elif self.tt_validity == 'year':
                api_expired_date = api_create_date + relativedelta(years=self.tt_number)
                refresh_expired_date = refresh_create_date + relativedelta(years=self.tt_number)
            else:
                api_expired_date = False
                refresh_expired_date = False
        elif api_date and refresh_date:
            api_expiry = int(self.env["ir.config_parameter"].sudo().get_param("tt_odoo_rest_api.tt_api_expire"))
            refresh_expiry = int(self.env["ir.config_parameter"].sudo().get_param("tt_odoo_rest_api.tt_refresh_expire"))
            api_expired_date = api_create_date + timedelta(seconds=api_expiry)
            refresh_expired_date = refresh_create_date + timedelta(seconds=refresh_expiry)
        else:
            api_expired_date = False
            refresh_expired_date = False

        if api_date is None and refresh_date is None:
            self.tt_expired_date = api_expired_date
            self.tt_refresh_expired_date = refresh_expired_date
        else:
            return {'tt_expired_date': api_expired_date, 'tt_refresh_expired_date': refresh_expired_date}

    def tt_generate_api_key(self):
        api_token = uuid4().hex
        refresh_token = uuid4().hex
        self.tt_api_token = api_token
        self.tt_refresh_token = refresh_token

    def _auto_check_expiry(self):
        self = self.search([])
        for rec in self:
            if rec.tt_expired_date < fields.Datetime.now() or rec.tt_refresh_expired_date < fields.Datetime.now():
                rec.tt_is_expired = True
            else:
                rec.tt_is_expired = False


class TortecsRestAPIAccess(models.Model):
    _name = 'tortecs.rest.api.rule'
    _description = 'Tortecs Rest API Access'
    _rec_name = 'tt_name'

    tt_name = fields.Many2one("ir.model", string="Model", ondelete="cascade")
    tt_rest_api_id = fields.Many2one('tortecs.rest.api', string='API ID')
    tt_create = fields.Boolean('Create')
    tt_write = fields.Boolean('Update')
    tt_read = fields.Boolean('Read')
    tt_delete = fields.Boolean('Unlink')
