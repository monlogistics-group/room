# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Javkha. 2022-12-01

from odoo import api, fields, models

class BudgetDataModel(models.Model):
    _name = "mltrucking.budget.data"
    _description = "ML Trucking budget data model"
    
    locale = fields.Many2one(string="Language",comodel_name='res.lang',domain=['|', ('active', '=', False), ('active', '=', True)])
    ceo=fields.Char(string='CEO')
    title=fields.Char(string='Title')
    name=fields.Char(string='Name')
    es_time=fields.Char(string='Estimated time')
    chassis_num=fields.Char(string='Chassis number')
    position=fields.Char(string='Position')
    from_to=fields.Char(string='From TO')
    task=fields.Char(string='Task')
    net_distance=fields.Char(string='Net Distance')
    total_distance=fields.Char(string='Total Distance')
    tr_num=fields.Char(string='Trasnportation Number')
    purpose=fields.Char(string='Purpose')
    quantity=fields.Char(string='Quantity')
    cost=fields.Char(string='Cost')
    subtotal=fields.Char(string='Subtotal')
    total_cost=fields.Char(string='Total cost')
    profession_budget=fields.Char(string='Profession')
    review=fields.Char(string='Review')
    ceo_name=fields.Char(string='Ceo name')



