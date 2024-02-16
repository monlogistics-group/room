# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2023-1-4

from email.policy import default
from odoo import api, fields, models
class SearchWizard(models.TransientModel):
    _name = 'freight.search.wizard'
    
    helper_id = fields.Char()

    type=fields.Many2many(comodel_name='freights.type' ,string='Type')
    ability= fields.Many2many(comodel_name='freights.ability',string='Ability')

    country = fields.Many2one(comodel_name='res.country' , string='Country')
    
    agent_rating = fields.Float(string='Agent Rating')
    
    # filterdene 
    def filter_freights_agent_inquiry(self):
        domain =""
        domainarr = []
        # domainarr.append("('agent','=', True)")
        domainarr.append("('company_type','=', 'company')")
        if self.ability:
            ab_id = []
            for t in self.ability:
                ab_id.append(str(t.id))
            domainarr.append("('freigths_abilities.id','in', %s)" % ("[" + ','.join([str(elem) for elem in ab_id]) + "]"))
        if self.type:
            type_id = []
            for t in self.type:
                type_id.append(t.id)
            domainarr.append("('freigths_type.id','in', %s)" % ("[" + ','.join([str(elem) for elem in type_id]) + "]"))
        if self.country:
            domainarr.append("('country_id.id', '=', '%s')" % (self.country.id))
        if self.agent_rating:
            domainarr.append("('agent_rating', '>=', '%s')" % {self.agent_rating})
        domain = "[" + ','.join([str(elem) for elem in domainarr]) + "]"
        context = self._context.copy()
        context['parent_id'] = self.helper_id
        res_partner_tree_view = self.env.ref('ml_worldwide-main.res_partner_new_tree_view').id
        print(res_partner_tree_view,'=====')
        filtered = {
            'name': 'Filtered tree view',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'view_type': 'form',
            'res_model': 'res.partner',
            'views' : [(res_partner_tree_view,'tree')],
            'view_id': False,
            'domain': domain,
            'target' : 'new',
            'context' : context
        }
        return filtered
 