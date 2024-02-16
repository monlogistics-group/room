from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import  ValidationError

class FreightRoutesShipments(models.Model):
    _name = 'freights.route.shipment'
    _description = 'Routes'
    _order = 'sequence,shipment_id asc'

    route_point_new = fields.Many2one(comodel_name="freights.route", string="Point")
    sequence = fields.Integer(related='route_point_new.sequence')
    route_point = fields.Many2one(comodel_name="freights.points", string="Point")
    shipment_id = fields.Many2one(comodel_name="freights.shipments", string="shipment")
    freights_id = fields.Many2one(comodel_name="mlworldwide.freights", string="Freight", ondelete='cascade')
    # zasah route ssequence soligdoh uyed daraalal soligdohgui bna
    etd_date = fields.Date(string="ETD", help="Expected time departure")
    atd_date = fields.Date(string="ATD", help="Actual time departured")
    eta_date = fields.Date(string="ETA", help="Expected time arival")
    ata_date = fields.Date(string="ATA", help="Actual time arrived")
    date_diff = fields.Integer(compute ="calculate_date")

    def calculate_date(self):
        if len(self.freights_id.freights_routes_shipment) > 0:
            d1=datetime.strptime(str(self.freights_id.freights_routes_shipment[0].etd_date),'%Y-%m-%d %H:%M:%S') 
            d2=datetime.strptime(str(self.freights_id.freights_routes_shipment[len(self.freights_id.freights_routes_shipment)-1].ata_date),'%Y-%m-%d %H:%M:%S')
            d3=d2-d1
            self.date_diff=str(d3.days)


    # def write(self, vals):
    #     print(vals,'===')
    #     res = super(FreightRoutesShipments, self).write(vals)
    #     return res

    # atd_date uurchlugduh vyd state-vdig on-going bolgono
    @api.onchange('atd_date')
    def _onchange_atd_date_field(self):
        print("wowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwow")
        if len(self.freights_id.freights_routes_shipment) > 0:
            print("wowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwow")
            if self.atd_date and self.sequence == 0:
                print("wowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwowwow")
                self.freights_id.state_id = 'on-going'  

            for shipment in self.freights_id.freights_shipment:
                if shipment.shipment_type_id.name == 'Container':
                    container_move = self.env['freights.container.movement'].search([('container_num', '=', shipment.container_type_id.id)])
                    for rec in container_move:
                        rec.state_id = 'ongoing'
                for package in shipment.shipment_packages:
                    package.state_id = 'on-going'
        
    ############################################ ! ETD g uurchulhud busadiih ni ETD dagaj uurchlugduud baisan tul commentlloo #####################################################
    # @api.onchange('etd_date')
    # def _onchange_etd_date_field(self):
    #     etd=self.freights_id.freights_routes_shipment
    #     for shipment in etd:
    #         if self.shipment_id.track_number == shipment.shipment_id.track_number:
    #             shipment.etd_date = self.etd_date
    #         # for in shipment

    @api.onchange('ata_date')
    def _onchange_ata_date_field(self):
        print("count started")
        length = len(self.freights_id.freights_shipment)
        checker = 0
        print("length ", length)
        maxseq = 0
        for routes_shipment in self.freights_id.freights_routes_shipment:
            if maxseq < routes_shipment.sequence:
                maxseq = routes_shipment.sequence
        print(maxseq)
        for routes_shipment in self.freights_id.freights_routes_shipment:
            if routes_shipment.ata_date and routes_shipment.sequence == maxseq:
                checker += 1
        if self.ata_date and checker + 1 == length:
            checker += 1
        print("checker ", checker)
        if checker == length:
            self.freights_id.state_id = 'arrived'
        for rec in self.shipment_id.shipment_packages:
            rec.state_id = 'arrived'

        arr = []
        for shipment in self.freights_id.freights_routes_shipment:
            if shipment.shipment_id.name == self.shipment_id.name:
                arr.append(shipment.id)

        if self._origin.id == arr[len(arr)-1]:
            emails = []
            for shipment in self.freights_id.freights_routes_shipment:
                if shipment.id == self._origin.id:
                    if shipment.shipment_id != False:
                        for package in shipment.shipment_id.shipment_packages:
                            if package.consignee_id.id != False:
                                emails.append(package.consignee_id.email)
                            else:
                                raise ValidationError("There is no consignee")

            template_rec = self.env.ref('ml_worldwide-main.mlworlwide_arrival_notice')
            emails_to = ','.join([str(elem) for elem in emails])
            template_rec.write({
                'email_to' : emails_to,
                'auto_delete': False
            })
            template_rec.send_mail(self._origin.id, force_send=True) 

   
