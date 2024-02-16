from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import  ValidationError

class FreightRoutesShipmentsWizard(models.TransientModel):
    _name = 'freights.route.shipment.wizard'

    #####  freights_id
    # def freights_route_shipmments(self):
    #     get_freight_base_id = self.env.context.get('default_freight_id')
    #     get_freight_base = self.env['mlworldwide.freights'].browse(get_freight_base_id)
    #     return get_freight_base.freights_routes_shipment
    
    # def _get_freights_route_shipment(self):
    #     arr = []
    #     freight = self.env["mlworldwide.freights"].browse(self.env.context.get('default_freight_id'))
    #     for rec in freight.freights_routes_shipment:
    #         arr.append(rec.id)
    #     return "[('freights_id.freights_routes_shipment.id','in', {})]".format(arr)
    
    def freights_routes_f(self):
        get_freight_base_id = self.env.context.get('default_freight_id')
        get_freight_base = self.env['mlworldwide.freights'].browse(get_freight_base_id)
        if get_freight_base.freights_route:
            return get_freight_base.freights_route[0]
        else:
            return []
    
    def _get_freights_routes(self):
        arr = []
        freight = self.env["mlworldwide.freights"].browse(self.env.context.get('default_freight_id'))
        for rec in freight.freights_route:
            arr.append(rec.id)
        print("arr", arr)
        return "[('freights_id.freights_route.id','in', {})]".format(arr)
    
    def freights_shipmments_f(self):
        get_freight_base_id = self.env.context.get('default_freight_id')
        get_freight_base = self.env['mlworldwide.freights'].browse(get_freight_base_id)
        return get_freight_base.freights_shipment
    
    def _get_freights_shipment(self):
        arr = []
        freight = self.env["mlworldwide.freights"].browse(self.env.context.get('default_freight_id'))
        for rec in freight.freights_shipment:
            arr.append(rec.id)
        return "[('freights_id.freights_shipment.id','in', {})]".format(arr)

    custom_date = fields.Date(string="Date", help="Custom date")
    # freights_routes_shipments = fields.Many2many(comodel_name="freights.route.shipment", string="Shipmments", default=freights_route_shipmments, domain=_get_freights_route_shipment)
    freights_routes = fields.Many2one(comodel_name="freights.route", string="Route points", default=freights_routes_f, domain=_get_freights_routes)
    check_all = fields.Boolean(default=True, string="Select All")
    freights_shipments = fields.Many2many(comodel_name="freights.shipments", string="Shipments", default=freights_shipmments_f, domain=_get_freights_shipment)
    def create_dates(self):
        print("freight_id")
        print(self.env.context.get('default_freight_id'))
        print(self.custom_date)
        if len(self.freights_shipments) == 0:
            raise ValidationError("Please select shipmens")
        if self.custom_date == False:
            raise ValidationError("Please select date")
        arr = []
        for rec in self.freights_shipments:
            arr.append(rec.id)

        get_freight_base_id = self.env.context.get('default_freight_id')
        get_freight_base = self.env['mlworldwide.freights'].browse(get_freight_base_id)
        print(get_freight_base.freights_routes_shipment)
        if self.env.context.get('default_type_date') == "ATA":
            for rec in get_freight_base.freights_routes_shipment:
                if rec.shipment_id.id in arr and rec.route_point_new.id == self.freights_routes.id:
                    rec.ata_date = self.custom_date
        elif self.env.context.get('default_type_date') == "ETA":
            print("aaaa")
            for rec in get_freight_base.freights_routes_shipment:
                print(rec.shipment_id, arr,rec.route_point_new, self.freights_routes.id)
                if rec.shipment_id.id in arr and rec.route_point_new.id == self.freights_routes.id:
                    print("bbb")
                    rec.eta_date = self.custom_date
        elif self.env.context.get('default_type_date') == "ATD":
            for rec in get_freight_base.freights_routes_shipment:
                if rec.shipment_id.id in arr and rec.route_point_new.id == self.freights_routes.id:
                    rec.atd_date = self.custom_date
        elif self.env.context.get('default_type_date') == "ETD":
            for rec in get_freight_base.freights_routes_shipment:
                if rec.shipment_id.id in arr and rec.route_point_new.id == self.freights_routes.id:
                    rec.etd_date = self.custom_date    

    @api.onchange('check_all')
    def _onchange_check_all(self):
        if self.check_all:
            print("Yes")
            get_freight_base_id = self.env.context.get('default_freight_id')
            get_freight_base = self.env['mlworldwide.freights'].browse(get_freight_base_id)
            self.freights_shipments = get_freight_base.freights_shipment
        else:
            print("No")
            self.freights_shipments = [(5,0,0)]