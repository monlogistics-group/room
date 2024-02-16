
import datetime
from email.policy import default
from odoo import api, fields, models, _
import requests
import json

class FreightsAgentInquiryModel(models.Model):
    _name = 'freights.agent.inquiry'
    _description = 'Agent inquiry'

    def _get_origin_point(self):
        freight = self.env["mlworldwide.freights"].browse(self.env.context.get('default_freight_id'))
        return freight.origin_point_id

    def _get_destination_point(self):
        freight = self.env["mlworldwide.freights"].browse(self.env.context.get('default_freight_id'))
        return freight.destination_point_id
    
    def _get_taras_ids(self):
        freight = self.env["mlworldwide.freights"].browse(self.env.context.get('default_freight_id'))
        res = []
        for ttype in freight.taras_id:
            res.append(ttype.id)
        return [('id', 'in', res)]
    
    def _get_default_domain_freight_type(self):
        freight = self.env["mlworldwide.freights"].browse(self.env.context.get('default_freight_id'))
        res = []
        for ttype in freight.freigths_type:
            res.append(ttype.id)
        return json.dumps([('id', 'in', res)])

    
    def _get_default_domain_fcl_route(self):
        freight = self.env["mlworldwide.freights"].browse(self.env.context.get('default_freight_id'))
        res = []
        for ttype in freight.fclroute_ids:
            res.append(ttype.id)
        return json.dumps([('id', 'in', res)])
    
    # def freights_id_default(self):
    #     get_freight_base_id = self.env.context.get('default_freight_id')
    #     get_freight_base = self.env['mlworldwide.freights'].browse(get_freight_base_id)
    #     return get_freight_base.id

    name = fields.Char(string="Name")
    gross=fields.Float(string="Gross(cbm)")
    volume=fields.Float(string="Volume(Kg)")
    remark = fields.Char('Remark')
    show_tara = fields.Boolean(default=False)
    show_volgross = fields.Boolean(default=False)
    freight_type_domain = fields.Char(default=_get_default_domain_freight_type)
    fcl_route_domain = fields.Char(default=_get_default_domain_fcl_route)
    
    agent_id = fields.Many2many(comodel_name="res.partner", string="Agent", help="Захиалга өгсөн менежерийн нэр",) 
    taras_id = fields.Many2many('freights.taras', string='Taras')
    agent_costs_ids = fields.Many2many(comodel_name="freights.agent.cost", string="Agent costs", help="")

    route_id = fields.Many2one(comodel_name="freights.route.category", string="FCL Route", help="FCL Route") 
    container_type=fields.Many2one(comodel_name="freights.container.type", string="Container type", help="Container type")
    shipping_line=fields.Many2one(comodel_name="freights.shipping.line", string="Shipping line", help="Container type")
    freights_id = fields.Many2one(comodel_name="mlworldwide.freights", string="Freight", ondelete='cascade')
    origin_point_id = fields.Many2one('freights.points', string='Origin Point',default=_get_origin_point, )
    destination_point_id = fields.Many2one('freights.points', string='Destination Point', default=_get_destination_point, )
    freigths_type = fields.Many2one(comodel_name="freights.type", string="Type", help="Freights type") 
    checker = fields.Boolean()
    
    def _compute_domain_freight_type(self):
        for rec in self:
            print("aaaaaaaaaaaaaaaaaa", rec, self.freights_id)
            res = []
            for ttype in rec.freights_id.freigths_type:
                res.append(ttype.id)
            print(res)
            rec.freight_type_domain = json.dumps([('id', 'in', res)])



    def _compute_domain_fcl_route(self):
        for rec in self:
            res = []
            for ttype in rec.freights_id.fclroute_ids:
                res.append(ttype.id)
            rec.fcl_route_domain = json.dumps([('id', 'in', res)])

    # @api.onchange("freights_id")
    # def _onchange_freights_id(self):
    #     self._compute_domain_freight_type()
    #     self._compute_domain_fcl_route()
    
    @api.onchange("freigths_type")
    def _onchange_freights_type(self):
        res = False
        volgross = False
        typname = str(self.freigths_type.type_name).upper()
        if typname == "FCL":
            res = True
            
        if typname == "LCL" or typname == "LTL" or typname == "AIR" or typname == "TRAIN" or typname == "WGN" or typname == "MULTIMODAL":
            volgross = True

        freight = self.env["mlworldwide.freights"].browse(self.env.context.get('default_freight_id'))
        if volgross:
            self.gross = freight.gross
            self.volume = freight.volume
        if res: 
            self.taras_id = freight.taras_id
        self.show_tara = res
        self.show_volgross = volgross
    
    def action_inquiry_email_send(self):
        base_id=self.env.context.get('default_freight_id')
        base_freight = self.env['mlworldwide.freights'].search([('id', '=', base_id)])
        base_freight.ctx = self.id
        self.ensure_one()
        template = self.env.ref('ml_worldwide-main.mail_template_data_agent_inquiry')
        if not self.origin_point_id.id or not self.destination_point_id.id or not self.freights_id.id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'title': 'Warning',
                    'message': 'In order to send a email, you have to fill all the fields!',
                    'sticky': False,
                    }
            }
        subject ="RATE INQUIRY / " 
        if  base_freight.origin_point_id.id == self.origin_point_id.id:
            subject += self.origin_point_id.name
            subject += ','
            subject += base_freight.origin_term.code       
        else:
            subject +=self.origin_point_id.name
        subject += '-'    
        if  base_freight.destination_point_id.id == self.destination_point_id.id:
            subject += self.destination_point_id.name
            subject += ','
            subject += base_freight.destination_term.code       
        else:
            subject +=self.destination_point_id.name    
        subject+= ' /'
        subject+= ' '
        subject+= base_freight.ref_num                    
        base_freight.agent_inquiry_mail_subject = subject
        ctx = {
            'default_model': 'freights.agent.inquiry',
            'default_res_id': self.id,
            'default_use_template': bool(template.id),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
            'force_email': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def update_or_add_agents(self):
        wizard = self.env['freight.search.wizard'].create({
            'helper_id' : self.id,
        })
        return {
            'name': ('Filter conditions'),
            'type': 'ir.actions.act_window',
            'res_model': 'freight.search.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new'
        }