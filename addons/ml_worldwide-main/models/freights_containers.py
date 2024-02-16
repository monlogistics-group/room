from odoo import api, fields, models, _


class FreightContainers(models.Model):
    _name = 'freights.containers'
    _description = 'Containers'

    # COC, SOC, TRANSFER
    name = fields.Char(string='Number')
    weight = fields.Char(readonly=True)
    freedays = fields.Integer(string='Free days')
    
    container_type_id = fields.Many2one(comodel_name='freights.container.type', string="Container type", domain=[('active', '=', True)])
    container_type_id_name = fields.Char(related='container_type_id.name', string="Container type Name")
    taras_id = fields.Many2one(comodel_name='freights.taras', string="Tara", domain=[('active', '=', True)])
    taras_id_name = fields.Char(related='taras_id.name')
    owner_id = fields.Many2one(comodel_name='res.partner', string="Owner")
    shipiing_line_id = fields.Many2one(comodel_name='freights.shipping.line', string="Shipping line")
    demmurate_start_point_id = fields.Many2one(comodel_name='freights.points', string="Demmurage start point")
    demmurate_end_point_id = fields.Many2one(comodel_name='freights.points', string="Demmurage end point")
    terminal_id = fields.Many2one(comodel_name='freights.terminal', string="Terminal")
    
    @api.onchange('taras_id')
    def _evaluate_weight(self):
        if self.taras_id.name == '20':
            self.weight = "2400"
        elif self.taras_id.name == "40":
            if self.taras_id.name == "45FR" or self.taras_id.name == "45RF":
                self.weight = "7100"
            self.weight = "4800"
        else:
            self.weight = "7100"
        print(self.weight,'------')

    # busad ireeduid heregtei Fields
    # terminalATA
    # Inconsignee date
    # return terminal date
    # sularsan ognoo
    # hooson achsan ognoo
    # hil deer ochson ognoo
    # demuurage duusah tseg deer ochson ognoo
    # shiljuulsen
    # tureeslesen date
    # Zarsan

    # Hooson butsaah UBTZ form fields (mash olon field buglunu)

    # Mun teevert yavj baigaa bolon teever duussan esehiig medeh status hereg boloh bh