from odoo import api, fields, models

class FreightIncexcService(models.Model):
    _name = 'freight.incexc.service'
    
    def _lang_get(self):
        langs = self.env['res.lang'].get_installed()
        return langs

    name=fields.Char(string="Name")
    isincluded = fields.Boolean(default="False")
    locale = fields.Selection(string="Language", selection=_lang_get, domain=['|', ('active', '=', False), ('active', '=', True)])
    quotation_id = fields.Many2one("freights.quotations", string="Quotation",ondelete='cascade',) #, required = True, readonly=True)
    
    @api.model
    def create(self, values):
        result = super(FreightIncexcService, self).create(values)
        # print(result.quotation_id.freights_incude_service , '-1--re')
        if result.isincluded:
            result.quotation_id.freights_incude_service += result
        else:
            result.quotation_id.freights_exclude_service += result
        # print(result,'result-')
        return result
        # TODO window iig khaakh

    def action_close(self):
        return {'type': 'ir.actions.act_window_close'}

    @api.onchange('template_id')
    def _onchange_template_id(self):
        for rec in self:
            if rec.template_id:
                rec.name = rec.template_id.name
                rec.isincluded = rec.template_id.isincluded
    def action_move_include(self):
        # quotations = self.env['freights.quotations'].browse(self.env.context.get('default_quotation_id'))
        # isinc = not self.isincluded
        # self.sudo().write({
        #             'isincluded': not self.isincluded,
        #         })
        for rec in self:
            rec.isincluded = not rec.isincluded
        return True    
            
    def action_remove_include(self):
        self.unlink()
                            
    def action_move_exclude(self):
        # quotations = self.env['freights.quotations'].browse(self.env.context.get('default_quotation_id'))   
        # isinc = not self.isincluded
        # self.sudo().write({
        #             'isincluded': not self.isincluded,
        #         })
        for rec in self:
            rec.isincluded = not rec.isincluded
        return True        
    def action_remove_exclude(self):
        self.unlink()

class FreightIncexcServiceTemplate(models.Model):
    _name = 'freight.incexc.service.template'

    def _lang_get(self):
        langs = self.env['res.lang'].get_installed()
        return langs

    locale = fields.Selection(string="Language", selection=_lang_get, domain=['|', ('active', '=', False), ('active', '=', True)])
    name=fields.Char(string="Name")
    isincluded = fields.Boolean(default="False")
    quotation_id = fields.Many2one("freights.quotations", string="Quotation", ondelete='cascade') #, required = True, readonly=True)

    countries = fields.Many2one('res.country', 'Country')

    origin_terms = fields.Many2many('origin.incoterms','origin_origin_terms_template', "origin_terms_id",string='Origin term')
    destination_terms = fields.Many2many('destination.incoterms','destination_destination_terms_template', "destination_terms_id", string='Destination term')  
    incexc_freight_types=fields.Many2many(comodel_name='freights.type', string="Inc freight types")
    fcl_route = fields.Many2many('freights.route.category', string='FCL Routes', store=True)
    service_types=fields.Many2many('freights.service.type', string='Service type')

    def _lang_get(self):
        langs = self.env['res.lang'].get_installed()
        return langs
    locale = fields.Selection(string="Language", selection=_lang_get, domain=['|', ('active', '=', False), ('active', '=', True)])
    
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, '%s - %s' % (str(rec.id), str(rec.id))))
        return result

    
        
