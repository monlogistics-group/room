from odoo import models, fields

class ContainerYard(models.Model):
    _name = "container.yard"

    name=fields.Char(string='name')
   