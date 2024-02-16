import json
from odoo import api, fields, models, _
import base64
class FreightShipments(models.Model):
    _name = 'freights.shipments'
    _description = 'Shipments'
    _rec_name = "name"

    freights_id = fields.Many2one(comodel_name="mlworldwide.freights", string="Freight", ondelete="cascade")
    name = fields.Char(string='Number')
    shipment_type_id_related = fields.Char(related='shipment_type_id.name')
    booking_number =  fields.Char(string='Booking number')
    track_number =  fields.Char(string='Truck number', )
    shipment_data = fields.Char(compute='_compute_consegn_names')

    shipment_type_id = fields.Many2one(comodel_name='freights.shipment.type', string="Trucking type", domain=[('active', '=', True)])
    container_type_id = fields.Many2one(comodel_name='freights.containers', string="Container")
    container_type_id_name = fields.Char(related='container_type_id.container_type_id_name', string="Container Type")
    taras_id_name = fields.Char(related='container_type_id.taras_id_name', string="Container Type")
    cargo_currency_id = fields.Many2one(comodel_name='res.currency', string="Currency", domain=[('active', '=', True)], default=lambda self: self.env.company.currency_id)
    vehicle = fields.Many2one(comodel_name='fleet.vehicle', string='Vehicle')
    # freights_id = fields.Many2one(comodel_name="mlworldwide.freights", string="Freight", ondelete='cascade')
    # container_details = fields.Many2one(comodel_name='freight.container.details')

    cargo_price = fields.Float(string='Cargo price')

    shipment_packages = fields.One2many('freights.packages','number_id')
    records_count = fields.Integer(compute="_count_records")
        
    remark = fields.Text(string='Remark')

    insurance_ids = fields.One2many('freight.insurance', 'shippment_id', string='Insurance',)

   


    @api.depends("shipment_packages")
    def _count_records(self):
       for rec in self:
           rec.records_count = len(rec.shipment_packages)

    def _default_terminal_id(self):
        freight = self.env["mlworldwide.freights"].browse(self.env.context.get('default_freight_id'))
        return freight.terminal_id.id

    terminal_id = fields.Many2one('freights.terminal', 'Terminal', default=_default_terminal_id)
    vehicle_show=fields.Boolean(default=False, help="Show")
    container_show=fields.Boolean(default=False, help="Show")


    

    @api.onchange('shipment_type_id')
    def _onchange_shipment_type_id(self):
        self.container_show = False
        self.vehicle_show = False
        if self.shipment_type_id.name == 'Container':
            self.container_show = True
            self.vehicle = [(5,0,0)]
        elif self.shipment_type_id.name == 'Vehicle':
            self.vehicle_show = True
            self.container_type_id = [(5,0,0)]
        else:
            self.container_type_id = [(5,0,0)]
            self.vehicle = [(5,0,0)]
        
        
    @api.onchange('shipment_packages')
    def _onchange_shipment_packages(self):
        print(self._origin.id,'------=======')

    @api.depends('shipment_packages.consignee_id')
    def _compute_consegn_names(self):
        for record in self:
            sh_da = ""
            for shs in record.shipment_packages:
                sh_da += str(shs.consignee_id.name) or ""
                sh_da += '||' + str(shs.consignee_phone)  or ""
                sh_da += '||' + str(shs.name) or ""
                sh_da += '||' + str(shs.referral) or ""
                sh_da += '||' + str(shs.release_note_remark) or ""
                sh_da += '||' + str(shs.package_qty)
                sh_da += '||' + str(shs.volume)
                sh_da += '||' + str(shs.gross)
                sh_da += '||' + str(shs.state_id)
            record.shipment_data = sh_da

    @api.onchange('vehicle')
    def _oncgange_vehicle_id(self):
        for rec in self:
            rec.track_number = rec.vehicle.name
            rec.name = rec.vehicle.name

    # container_type_id uurchlugdwul track_number fielded utga onoono
    @api.onchange('container_type_id')
    def _onchange_container_type_id(self):
        for rec in self:
            rec.track_number = rec.container_type_id.name
            rec.name = rec.container_type_id.name

    def delete_item(self):
        for rec in self.freights_id.freights_payments:          
            for rs in rec.shippment_ids:
                if self.id == rs.id:
                    rec.unlink()
        for rec in self.freights_id.freights_routes_shipment:          
            for rs in rec.shipment_id:
                if self.id == rs.id:
                    rec.unlink()
        print(self,'----------')
        self.unlink()
    
    # def copy_data(self, default=None):
    #     defaults = super().copy_data(default=default)
    #     if 'from_duplicate' in self.env.context and self.env.context.get('from_duplicate'):
    #         return [{k: v for k, v in default.items()} for default in defaults]
    #     else:
    #         return [{k: v for k, v in default.items() if k in self.SELF_READABLE_FIELDS} for default in defaults]

    def duplicate_item(self):
        self.ensure_one()

        duplicate_rec = self.copy()
        


    @api.model
    def create(self, values):
        print(values,'create---------')
        if 'freights_id' in values:
            if values['freights_id']:
                fid = 0
                if isinstance(values['freights_id'], int):
                    fid = values['freights_id']
                else:
                    fid = values['freights_id'].id
                
                print("values['freights_id']", values['freights_id'])
                freight = self.env['mlworldwide.freights'].search([('id', '=', fid)])
                if 'container_type_id' in values:
                    if values['container_type_id']:
                        self.env['freights.container.movement'].create({
                            'freights_id' : freight,
                            'container_num' : values['container_type_id']
                        })
                    else:
                        self.env['freights.container.movement'].create({
                            'freights_id' : freight,
                        })
        shipment_id=super(FreightShipments, self).create(values)
        if 'freights_id' in values:
            if values['freights_id']:
                fid = 0
                if isinstance(values['freights_id'], int):
                    fid = values['freights_id']
                else:
                    fid = values['freights_id'].id
                freight = self.env['mlworldwide.freights'].search([('id', '=', fid)])
                if len(freight.freights_shipment) == 1:
                    for rec in freight.freights_quotations:
                        if rec.state_id == 'confirmed':
                            rec.create_payments(rec.freights_id, rec.service_ids)
                            freight.shipment_calc()
                            package = self.env['freights.packages'].create({
                                'name' : freight.notes,
                                'consignee_id' : freight.customer_id.id,
                                'package_qty': freight.package_qty,
                                'number_id' : shipment_id.id
                            }) 
                            if freight.volume:
                                package.write({
                                    'volume' : freight.volume
                                })
                            if freight.gross:
                                package.write({
                                    'gross' : freight.gross
                                })
                            shipment_id.write({
                                'shipment_packages' : package
                            })
                else:
                    print("-------------5")
                    res = self.env['freights.payment.service'].search([('shippment_ids', '=', freight.freights_shipment[0].id), ('freights_id', '=', freight.id)])
                    respack = self.env['freights.packages'].search([('number_id', '=', freight.freights_shipment[0].id)])
                    print("res", shipment_id)
                    if res:
                        for rec in res: 
                            freight.freights_payments +=rec.copy({'shippment_ids': [shipment_id.id]})
                        freight.shipment_calc()
                    if respack:
                        for rec in respack:
                            shipment_id.shipment_packages +=rec.copy({'number_id': shipment_id.id})
                shipments_remark = self.env['freights.shipments.remark'].create({
                    'freights_id' : freight.id,
                    'freights_shipment' : shipment_id.id,
                }) 
        return shipment_id

    def action_insurance_data(self):
        print("action_insurance_data")
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'freight.insurance',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': {"default_shippment_id": self.id},
        }
    
    def action_insurance_register(self):
        print("action_insurance_register")
        return self.env['insurance.appendix'].register_insurance_cases(self.id)
        # data["shipment_id"] = self.id

        # return self.env.ref(
        #     "ml_worldwide.action_insurance_register"
        # ).report_action(self, data=data)