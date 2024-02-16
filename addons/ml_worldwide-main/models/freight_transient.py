
from datetime import datetime, timedelta
from email.policy import default
from odoo import api, fields, models
class FreightTransient(models.TransientModel):
    _name = 'freight.transient'
    
    freight_id=fields.Many2many(comodel_name="mlworldwide.freights" , string="Freight transient")
    route_data = fields.Many2one(comodel_name='route.data',string="Route Data" )        

    @api.model
    def _autosend_route_info(self):
        ''' Ene functionoor customert automataar zamiin medeeg
        emaileer yabuulna.
        '''
        print("_autosend_route_info")
        self.env()
        
        freights = self.env["mlworldwide.freights"].search([("is_active_freights","=",True)])
        for freight in freights:
            for shipment in freight.freights_shipment:
                for package in shipment.shipment_packages:
                    if package.consignee_id:
                        cron_job = self.env['mlworldwide.cron.job'].search([])
                        
                        if len(cron_job) > 0:
                            for cr in cron_job:
                                if cr.customer_id.id == freight.customer_id.id:
                                    state = freight.state_id
                                    if  state == 'on-going':
                                        hour = False
                                        for hr in cron_job.cron_hours:
                                            if str(self.timezonetoUTC8(datetime.now()).hour) == hr.name:
                                                hour = True
                                        weekd = False
                                        for we in cron_job.cron_weekday:
                                            if str(self.timezonetoUTC8(datetime.now()).weekday()+1) == we.name:
                                                weekd = True
                                                if hour and weekd:
                                                    filtered_data=self.env['mlworldwide.freights'].search([('customer_id.name', '=',freight.customer_id.name),('state_id','=','on-going')])
                                           
                                                    helper_arr = []
                                                    for data in filtered_data:
                                                        helper_arr.append(data.id)
                                                    route_id = []
                                                    for data in self.env["route.data"].search([]):
                                                        route_id.append(data.id)
                                            
                                                    transient=self.create({"freight_id": helper_arr , 'route_data': route_id[0] })
                                                    template = self.env.ref("ml_worldwide-main.email_all_template_name")                    
                                                    template.send_mail(transient.id, force_send=True) 
                                                    break
                                                return True
    def timezonetoUTC8(self, date_from):
        return date_from + timedelta(hours=8)