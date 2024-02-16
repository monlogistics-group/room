# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-08-18
import json

from odoo import http
from odoo.http import request
from odoo.addons.auth_oauth.controllers.main import fragment_to_query_string

import logging
_logger = logging.getLogger(__name__)

class TruckingRestAPI(http.Controller):

    @http.route('/tracking/api/', type='http', auth="user", website=True)
    @fragment_to_query_string
    def tracking_api(self, access_token=False, long_lived_token=False, **kwargs):
        result = {"success":True, "msg":"Ok", "data":[]}
        return request.redirect('/web#menu_id=%s' % result)

    @http.route('/tracking/api/', type='json', methods=['GET', 'POST'], auth="public", website=True)
    def chatbothook(self, **kwargs):
        _logger.info("WEB HOOK ")
        if request.httprequest.method == 'GET':
            return 'Invalid verification request'
        else:
            return "Message Processed"
