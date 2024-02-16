from odoo import api, fields, models

class AddRecordToPayments(models.Model):
    _name = 'add.record.to.payments'
    _inherit = 'freights.payment.service'

    freights_id = fields.Many2one('mlworldwide.freights')
    package_id=fields.Many2one('freights.packages')
    shipment=fields.Boolean()
    package=fields.Boolean()


    def add_records(self):
        if not self.package :
            print(self.freights_id,'=')
            for rec in self.shippment_ids:
                self.freights_id.freights_payments += self.env['freights.payment.service'].create({
                    'shippment_ids' : rec,
                    'service_cost' : self.service_cost,
                    'service_rate' : self.service_rate,
                    'currency_id' : self.currency_id.id,
                    'agent_id' : self.agent_id.id,
                    'template_id' : self.template_id.id,
                    'service_from' : self.service_from.id,
                    'service_to' : self.service_to.id,
                    'service_qty' : self.service_qty,
                    'ett' : self.ett,
                    'valid_until_date' : self.valid_until_date,
                    'transport_type' : self.transport_type.id,
                    'service_desc' : self.service_desc,
                    'type' : self.type.id
                })
        else:
            for rec in self.shippment_ids:
                print(self.freights_id,'---=-')
                payment_service = self.env['freights.payment.service'].create({
                    'shippment_ids' : rec,
                    'service_cost' : self.service_cost,
                    'service_rate' : self.service_rate,
                    'currency_id' : self.currency_id.id,
                    'service_desc' : self.service_desc,
                    'type' : self.type.id
                })
                self.package_id.freights_payments += payment_service
                self.freights_id.freights_payments += payment_service
            
                