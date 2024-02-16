from odoo import api, fields, models, _

class FreightRoutes(models.Model):
    _name = 'freights.route'
    _description = 'Freight Routes'
    _order = 'sequence asc'

    sequence = fields.Integer(help="Used to order the note stages")
    
    point = fields.Many2one(comodel_name='freights.points',string='Point',ondelete='cascade')
    freights_id = fields.Many2one(comodel_name="mlworldwide.freights", string="Freight", ondelete='cascade')

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, '%s %s/%s' % (str(rec.sequence), str(rec.point.name), str(rec.point.country_code))))
            
        return result
    
    # def create(self, values):
    #     result = super(FreightRoutes, self).create(values) 
    #     print("result-----------------------------result")
    #     for rec in self.freights_id:
    #         rec.shipment_calc()
    #     return result
    
    # def write(self, values):
    #     result = super(FreightRoutes, self).write(values) 
    #     print("result-----------------------------result")
    #     for rec in self.freights_id:
    #         rec.shipment_calc()
    #     return result
    
    def delete_item(self):
        for rec in self.freights_id.freights_routes_shipment:          
            for rs in rec.route_point_new:
                if self.id == rs.id:
                    rec.unlink()
        self.unlink()


