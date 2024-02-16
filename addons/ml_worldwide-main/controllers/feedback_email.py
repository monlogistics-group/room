from odoo import http
from odoo.http import request
from datetime import date, datetime, timedelta

class RestApiRequests(http.Controller):

    @http.route('/feedback', auth='public',website=False, csrf=False, type='http')
    def index(self, **kw):
        if kw['agent_id']:
            is_existing = http.request.env['freights.client.feedback'].search([('agent_id','=', int(kw['agent_id']))],limit=1) 
            if is_existing.expire_date == False:
                is_existing.sudo().write({
                        'rate' : kw['rate'],
                        'expire_date' : date.today()
                    })
            d1=datetime.strptime(str(is_existing.expire_date),'%Y-%m-%d') 
            d2=datetime.strptime(str(date.today()),'%Y-%m-%d')
            d3=d2-d1
            date_diff=str(d3.days)
            if int(date_diff) > 7:
                return 'Expired'
            return 'Created'
        else:
            return 'Sorry There is Agent'