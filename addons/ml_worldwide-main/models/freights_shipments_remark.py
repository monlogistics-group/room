import json
from odoo import api, fields, models, _, Command
import base64
class FreightShipmentsRemark(models.Model):
    _name = 'freights.shipments.remark'
    _description = 'Shipments remark'

    freights_id = fields.Many2one(comodel_name="mlworldwide.freights", readonly=True,required=True,string="Freight", ondelete="cascade")
    freights_shipment = fields.Many2one(comodel_name='freights.shipments', readonly=True,required=True, ondelete="cascade")
    remark = fields.Html(string="remark")
    freights_delay_cat = fields.Many2one(comodel_name='freights.shipments.delay.category', string="Owner")
    freights_delay_reason = fields.Many2one(comodel_name='freights.shipments.delay', string="Issue")
    delay = fields.Html(string="Delay Remark")
    delay_days = fields.Integer(string="Delay",default=0)
    expected_actual = fields.Selection(selection=[
            ('expected', 'Expected'),
            ('actual', 'Actual'),
        ], default='expected', readonly=True, tracking=True)

    delay_domain = fields.Char(compute='_compute_delay_domain', readonly=True, store= True, )

    @api.depends('freights_delay_cat')
    def _compute_delay_domain(self):
        for rec in self:
            rec.delay_domain = json.dumps([('type.name', '=', rec.freights_delay_cat.name)])
    

