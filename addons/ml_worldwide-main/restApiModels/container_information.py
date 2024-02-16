

from odoo import api, fields, models, _

class ContainerInformation(models.Model):
    _name = "container.information"
    
    container_image = fields.Image(string = "Photo", help="зураг")
    title = fields.Char(string='Title')
    height = fields.Char(string='Height')


class DangerousGoods(models.Model):
    _name = "dangerous.goods"
    
    image = fields.Image(string = "Photo", help="зураг")
    title = fields.Char(string='Title')
    description = fields.Char(string='Description')

class WagonTypes(models.Model):
    _name = "wagon.types"
    
    image = fields.Image(string = "Photo", help="зураг")
    title = fields.Char(string='Title')
    height = fields.Char(string='height')

class WorldWideNews(models.Model):
    _name = "worldwide.news"
    
    image = fields.Image(string = "Photo", help="зураг")
    title = fields.Char(string='Title')
    description = fields.Char(string='description')
