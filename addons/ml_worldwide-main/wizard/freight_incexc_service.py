from odoo import api, fields, models

class FreightIncexcServiceWizard(models.Model):
    _inherit = 'freight.incexc.service'
    
    # def add_service_close(self):
    #     print("add_service_close", self)
        
    #     return {'type': 'ir.actions.act_window_close'}

    # @api.model
    # def create(self, values):
    #     result = super(FreightIncexcServiceWizard, self).create(values)
    #     if result.isincluded:
    #         result.quotation_id.freights_incude_service += result
    #     else:
    #         result.quotation_id.freights_exclude_service += result
    #     return result
        # TODO window iig khaakh