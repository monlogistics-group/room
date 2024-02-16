# -*- coding: utf-8 -*-
# Copyright 2022 Mon Logistics Group <https://www.mlholding.mn>
# Created by Umbaa. 2022-12-21

from odoo import fields, models

class WorldwideCronJob(models.Model):
    _name = "mlworldwide.cron.job"
    _rec_name = "customer_id"
    _description="Worldwide cron jobs"
    
    customer_id = fields.Many2one('res.partner')
    cron_weekday = fields.Many2many(comodel_name = "mlworldwide.cron.job.weekdays", string="Weekdays")
    cron_hours = fields.Many2many(comodel_name = "mlworldwide.cron.job.hours", string="Hours")
    


class WorldwideCronJobWeekdays(models.Model):
    _name = "mlworldwide.cron.job.weekdays"
    _description="Worldwide cron jobs weekdays"
    _rec_name = "name"

    name = fields.Char(required=True,)
    # weekday = fields.Selection(
    #     selection=[('1','Mon'),('2','Tue'),('3','Wed'),('4','Thu'),('5','Fri'),('6','Sat'),('7','Sun')], 
    #     string="Weekday", 
    #     help="Weekday"
    # )

class WorldwideCronJobHours(models.Model):
    _name = "mlworldwide.cron.job.hours"
    _description="Worldwide cron jobs hours"
    _rec_name = "name"

    name = fields.Char(required=True,)
    # hours = fields.Selection(
    #     selection=[('1','1'),
    #         ('2','1'),
    #         ('3','3'),
    #         ('4','4'),
    #         ('5','5'),
    #         ('6','6'),
    #         ('7','7'),
    #         ('8','8'),
    #         ('9','9'),
    #         ('10','10'),
    #         ('11','11'),
    #         ('12','12'),
    #         ('13','13'),
    #         ('14','14'),
    #         ('15','15'),
    #         ('16','16'),
    #         ('17','17'),
    #         ('18','18'),
    #         ('19','19'),
    #         ('20','20'),
    #         ('21','21'),
    #         ('22','22'),
    #         ('23','23'),
    #         ('0','0')], 
    #     string="Hours", 
    #     help="Hours"
    # )