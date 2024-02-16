# -*- coding: utf-8 -*-
# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-12-02

from odoo import fields, models

class WorldwideUserGroups(models.Model):
    _name = "mlworldwide.user.groups"
    _order = 'sequence asc'
    _rec_name = "name"
    _description="Worldwide create user group"

    name = fields.Char(string="User group name", required=True, translate=True)
    ref_name = fields.Char(string="Code", compute='compute_ref_name', readonly=True)
    sequence = fields.Integer(string="№", help="Used to order the note stages")

    _sql_constraints = [('mlworldwide_user_groups_name_unique', 'unique(name)', 'User group name already exists')]

    def compute_ref_name(self):
        for rec in self:
            rec.ref_name = rec.name.lower().replace(" ","_")