# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-11-16

import datetime
from email.policy import default
from odoo import api, fields, models
import requests
import json

class TruckingLocationModel(models.Model):
    _name = "mltrucking.location"
    _description = "ML Trucking Location model"
    _rec_name = 'date_locaion'
    _order = 'date_locaion asc'

    # truck_gps_id = fields.Char(string='GPS id',)
    truck_latitude = fields.Float('Geo Latitude', digits=(10, 7))
    truck_longitude = fields.Float('Geo Longitude', digits=(10, 7))
    truck_altitude = fields.Float('Geo Altitude', digits=(10, 7))
    fleet_id = fields.Many2one('fleet.vehicle', 'Truck', tracking=True, )
    #domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", help="Partner this case has been forwarded/assigned to.", index=True
    date_locaion = fields.Datetime(string="Location time", help="Ачаа огноо")
    truck_gps_params = fields.Char(string='Params',)

    def gps_location_update(self):
        print("HELLO GPS")
#5134d40096232e6d3a180baa1ea993602AF7DD2636168EA680D6146E018033CC1CAFA9C5
        config = self.env['mltrucking.location.config'].search([], limit=1)
        print(config.wialong_update_date)
        url = 'https://hst-api.wialon.com/wialon/ajax.html?svc=token/login&params={"token":"' + config.wialong_token + '"}'
        try:
            user = requests.get(url, {}).json()
            if user['au'] == config.wialong_user_name:
                get_msg_url = 'https://hst-api.wialon.com/wialon/ajax.html?svc=messages/load_interval&sid=' + user['eid'] + '&params='
                for item in json.loads(user['user']['prp']['monu']):
                    params='{"itemId":'+str(item)+',"timeFrom":'+str(int(datetime.datetime.timestamp(config.wialong_update_date)))+',"timeTo":'+str(int(datetime.datetime.timestamp(datetime.datetime.now())))+',"flags":1,"flagsMask":1,"loadCount":999}'
                    msgs = requests.get(get_msg_url + params, {}).json()
                    if msgs.get('messages'):
                        fleet = self.env["fleet.vehicle"].search([("truck_gps_id","=",item)], limit = 1)
                        for msg in msgs['messages']:
                            msg_params = dict({
                                "c":msg['pos']['c'],
                                "s":msg['pos']['s'],
                                "sc":msg['pos']['sc'],
                            } | msg['p']),
                            
                            self.env['mltrucking.location'].create({
                                'fleet_id':fleet.id,
                                'truck_latitude':msg['pos']['y'],
                                'truck_longitude':msg['pos']['x'],
                                'truck_altitude':msg['pos']['z'],
                                'date_locaion':datetime.datetime.fromtimestamp(msg['t']),
                                'truck_gps_params':json.dumps(msg_params)
                            })
            config.sudo().wialong_update_date = datetime.datetime.now()
            print(config.wialong_update_date)
        except Exception as e:
            self._raise_query_error(e)


class TruckingLocationConfigModel(models.Model):
    _name = "mltrucking.location.config"
    _description = "ML Trucking Location Config model"

    wialong_user_name = fields.Char(string='GPS user name',)
    wialong_user_pass = fields.Char(string='GPS password',)
    wialong_token = fields.Char(string='GPS token',)
    wialong_update_date = fields.Datetime(string="Location time", help="Last update date")