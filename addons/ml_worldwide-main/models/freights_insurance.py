# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# 
# Changed by Umbaa. 2023-06-07

from odoo import api, fields, models, _
from datetime import datetime

class FreightInsurance(models.Model):
    _name = 'freight.insurance'
    # _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _inherit = ['mail.thread']
    _description = 'Freight insurance'
    _rec_name = 'short_desc'
    
    # # freight.insurance.stage model -s ehniihig awna
    # def _get_default_stage_id(self):
    #     return self.env['freight.insurance.stage'].search([], order='sequence', limit=1)
    
    def _get_employee_id(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        return employee_rec.id 
    
    def shippment_id_default(self):
        get_id = self.env.context.get('default_shippment_id')
        return self.env['freights.shipments'].browse(get_id)
    
    shippment_id = fields.Many2one(comodel_name="freights.shipments", string="Shipment", default=shippment_id_default)
    short_desc = fields.Char('Short description', required=True,)
    description = fields.Text('Description')
    insurance_date = fields.Date('Date of insurance inspection')
    state_id = fields.Selection(selection=[
            ('state_id1', 'Даатгалаас хариу хүлээгдэж байгаа'),
            ('state_id2', 'Харилцагчаас бичиг баримт хүлээгдэж байгаа'),
            ('state_id3', 'Нөхөн төлбөр олгосон'),
            ('state_id4', 'Нөхөн төлбөр олгохоос татгалзсан'),
            ('state_id5', 'Харилцагчийн хүсэлтээр хаагдсан'),
            ('state_id6', 'ӨХХ болсон'),
            ('state_id7', 'Байгууллагын хариуцлагын даатгал'),
            ('state_id8', 'Харилцагчаас бичиг баримт ирүүлээгүй тул хаасан'),
            ('state_id9', 'ББ бүрдээгүй /3.2.16 заалт/'),
            ('state_id10', 'Даатгалгүй ачаа'),
            ('state_id11', 'Эрсдэлийн хороонд шилжүүлсэн'),
        ], default='state_id1', tracking=True)
    
    transfer_date = fields.Date('Date of Transfer to Insurer')
    transfer_note = fields.Text('Note of Transfer to Insurer')
    waiting_day = fields.Integer('Waiting Day')

    claim_amount = fields.Float('Claim amount', default=0.0)
    reimbursement_amount = fields.Float('Reimbursement amount', default=0.0)
    reimbursement_note = fields.Text('Note of Reimbursement')
    contract_note = fields.Char('Contractual Clause Refusal of Reimbursement')
    reimbursement_date = fields.Date('Date of Reimbursement')
    status_id = fields.Selection(selection=[
            ('closed', 'Хаагдсан'),
            ('open', 'Хаагдаагүй'),
        ], default='closed', tracking=True)
    
    closed_date = fields.Date('Date of closed Insurer')

    diff_amount = fields.Float('Difference Amount', compute="_compute_diff_amount", store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.company.currency_id.id)

    reimbursement_packages = fields.Many2one(comodel_name='freights.packages', string='Package')
    reimbursement_employee = fields.Many2one('hr.employee', string="Operation", default=_get_employee_id)

    # uniin zurvvg olno
    @api.depends('claim_amount', 'reimbursement_amount')
    def _compute_diff_amount(self):
        for obj in self:
            obj.diff_amount = obj.claim_amount - obj.reimbursement_amount
    
    @api.onchange('claim_amount', 'reimbursement_amount')
    def on_change_unit_amount(self):
        self._compute_diff_amount()

    # @api.model
    # def write(self, vals):
    #     print("FreightInsurance FreightInsurance FreightInsurance ")
    #     result = super(FreightInsurance, self).write(vals)
    #     if self.shippment_id:
    #         self.shippment_id.insurance_ids = result.id
    #     return result

#     company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
#                                  default=lambda self: self.env.company)
#     freights_id = fields.Many2one('mlworldwide.freights', 'Freights', required=True)
#     partner_id = fields.Many2one('res.partner', required=True)
#     user_id = fields.Many2one('res.users', 'TM user')
    

#     line_ids = fields.One2many('freight.insurance.line', 'insurance_id', 'Lines')

#     name = fields.Char('Name')
#     email = fields.Char('Email')
#     phone = fields.Char('Phone')
#     compensation_info = fields.Char('Compensation Info')
#     clause_info = fields.Char('Clause')
#     convert_info = fields.Char('Convert Info')

#     color = fields.Integer('Color')
#     waiting_day = fields.Integer('Waiting Day')
    
#     date = fields.Date('Date')
    
#     convert_date = fields.Date('Convert date')
#     pay_date = fields.Date('Payable Date')
    
#     amount = fields.Float('Invoice amount', default=0.0)
#     pay_amount = fields.Float('Pay amount', default=0.0)
#     diff_amount = fields.Float('Difference Amount', compute="_compute_diff_amount", store=True, readonly=True)
    
#     # uniin zurvvg olno
#     @api.depends('amount', 'pay_amount')
#     def _compute_diff_amount(self):
#         for obj in self:
#             obj.diff_amount = obj.amount - obj.pay_amount

#     # freight.insurance.stage model-n buh datag butsaana  
#     @api.model
#     def _read_group_freight_stage_ids(self, stages, domain, order):
#         stage_ids = self.env['freight.insurance.stage'].search([])
#         return stage_ids
    
#     # create hiih vyd name field-d utga onooono
#     @api.model
#     def create(self, values):
#         if not values.get('name', False) or values['name'] == _('New'):
#             values['name'] = self.env['ir.sequence'].next_by_code('freight.insurance')
#         return super(FreightInsurance, self).create(values)
    
#     def generate_insurance(self):
#         return True
    
# class FreightInsuranceLine(models.Model):
#     _name = 'freight.insurance.line'
#     _description = 'Freight insurance line'
    
#     company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
#                                  default=lambda self: self.env.company)
#     insurance_id = fields.Many2one('freight.insurance', 'Insurance')
#     shipment_id = fields.Many2one('freights.shipments', 'Shipment')
#     offset_id = fields.Many2one('freight.insurance.offset', 'Insurance Offset', required=True)

#     product_info = fields.Char('Product info')
#     loss_info = fields.Char('Loss info', required=True)
    
    
# class FreightInsuranceOffset(models.Model):
#     _name = 'freight.insurance.offset'
#     _description = 'Freight insurance Offset'
    
#     name = fields.Char('Insurance Offset')
    