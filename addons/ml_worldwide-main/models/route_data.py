from odoo import api, fields, models, _

class RouteData(models.Model):
    _name = 'route.data'
    

    freight_con = fields.Char(string='Freight condition')
    ltl = fields.Char(string='LTL')
    document=fields.Char(string="Document")
    sender = fields.Char(string='sender')
    officer= fields.Char(string='Officer')
    terminal_name=fields.Char(string='terminal')
    number=fields.Char(string='number')
    eta=fields.Char(string="ETA")
    etd=fields.Char(string="ETD")
    atd=fields.Char(string="ATD")
    ata=fields.Char(string="ATA")
    def _lang_get(self):
        langs = self.env['res.lang'].get_installed()
        return langs

    lang = fields.Many2one(string="Language",comodel_name='res.lang', domain=['|', ('active', '=', False), ('active', '=', True)])