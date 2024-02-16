# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-12-02
import json

from odoo import http
from odoo.http import request
from odoo.addons.auth_oauth.controllers.main import fragment_to_query_string

import logging
_logger = logging.getLogger(__name__)

class MLWorldwideRestAPI(http.Controller):

    @http.route('/worldwide/api/session_id', type='json', methods=['GET', 'POST'], auth="public", website=True)
    def get_session_id(self, **kwargs):
        _logger.info("WEB get_session_id ")
        request.session.check_security()
        request.uid = request.session.uid
        request.disable_db = False
        result = request.session
        result["session_id"] = str(request.httprequest.cookies.get('session_id'))
        return json.dumps(result)
    

    @http.route('/worldwide/api/', type='http', auth="user", website=True)
    @fragment_to_query_string
    def worldwide_api(self, access_token=False, long_lived_token=False, **kwargs):
        result = {"success":True, "msg":"Ok", "data":[]}
        return request.redirect('/web#menu_id=%s' % result)

    @http.route('/worldwide/api/', type='json', methods=['GET', 'POST'], auth="public", website=True)
    def worldwide_hook(self, **kwargs):
        _logger.info("WEB HOOK ")
        if request.httprequest.method == 'GET':
            return 'Invalid verification request'
        else:
            return "Message Processed"
