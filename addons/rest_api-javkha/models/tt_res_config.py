from odoo import fields, models


class TortecsResConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    tt_api_expire = fields.Integer('Enter the number for Expiry(in sec)',
                                   config_parameter='tt_odoo_rest_api.tt_api_expire')
    tt_refresh_expire = fields.Integer('Enter the number for Refresh Token Expiry(in sec)',
                                       config_parameter='tt_odoo_rest_api.tt_refresh_expire')

    def get_values(self):
        tt_res = super(TortecsResConfig, self).get_values()
        tt_res.update(
            tt_api_expire=self.env['ir.config_parameter'].sudo().get_param('tt_odoo_rest_api.tt_api_expire'),
            tt_refresh_expire=self.env['ir.config_parameter'].sudo().get_param('tt_odoo_rest_api.tt_refresh_expire')
        )
        return tt_res
