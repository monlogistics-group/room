# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime, timedelta
class FreightsTypeAssign(models.TransientModel):
    _name = 'freights.type.assign'
    _description = 'Freights Type Assign'

    freigths_type = fields.Many2many(comodel_name="freights.type", string="Type", help="Freights type",) 

    def assign_employees(self):
        print("assign_employees")
        freight = self.env["mlworldwide.freights"].browse(self.env.context.get('default_freight_id'))
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        arr = []
        for cntr in freight.contributor_ids:
            arr.append(cntr.role_name)
        for rec in self.freigths_type:
            if rec not in arr:
                checker = False
                employee_role = self.env['freights.employee.role'].search([('role_name', '=', rec.type_name)])
                for role in employee_role:
                    if employee_rec.id == role.employee.id:
                        checker = True
                if not checker:                        
                    freight.contributor_ids += self.env['freights.employee.role'].sudo().create({
                        'role_name':rec.type_name,
                        'employee':employee_rec.id
                    })
                else:
                    freight.contributor_ids += employee_role
                freight.freights_channel_id.sudo().channel_partner_ids += employee_rec.user_partner_id

        # employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
        # for group in employee.user_groups:
        #     if group.name.lower() == 'pd':
        #         grouped_country = self.env['res.country.group'].search([('name', '=', 'Asia')], limit=1)
        #         if grouped_country.country_ids.name:
        #             if freight.freights_route[0].point.name in grouped_country.country_ids.name:
        #                 end_date = self.get_due_date(datetime.now(), 8)
        #                 freight.date_store = end_date['end_date']
        #             else:
        #                 end_date = self.get_due_date(datetime.now(), 16)
        #                 freight.date_store = end_date['end_date']
        if (self.user_has_groups('ml_worldwide-main.group_mlworldwide_pd_manager') or self.user_has_groups('ml_worldwide-main.group_mlworldwide_pd')):
            grouped_country = self.env['res.country.group'].search([('name', '=', 'Asia')], limit=1)
            if grouped_country.country_ids.name:
                if freight.freights_route[0].point.name in grouped_country.country_ids.name:
                    end_date = self.get_due_date(datetime.now(), 8)
                    freight.date_store = end_date['end_date']
                else:
                    end_date = self.get_due_date(datetime.now(), 16)
                    freight.date_store = end_date['end_date']
        

    def get_due_date(self, start_date, hours):
        end_date = start_date
        if hours<40:
            if start_date.weekday()<(6-(hours/8)):
                """ Weekendgui """ 
                end_date = start_date + timedelta(days=int(hours/8))
            else:
                """ Weekend nemgdej baigaa """
                end_date = start_date + timedelta(days=2 + int(hours/8))
        else:
            new_hours = hours % 40
            if start_date.weekday()<(6-(new_hours/8)):
                """ Weekendgui """ 
                end_date = start_date + timedelta(days=int(new_hours/8)) + timedelta(days=int(hours % 40)*7)
            else:
                """ Weekend nemgdej baigaa """
                end_date = start_date + timedelta(days=2 + int(new_hours/8)) + timedelta(days=int(hours % 40)*7)

        """ holiday ehelsen bn uu ?"""
        holidays = self.env["hr.leave"].search(['&',('date_from', '>=', start_date),('date_from', '<=', end_date)])
        # if not holidays:
        holidays += self.env["hr.leave"].search(['&',('date_from', '<=', start_date),('date_to', '>=', end_date)])
            # if not holidays:
        holidays += self.env["hr.leave"].search(['&',('date_from', '<=', start_date),('date_to', '>=', start_date)])
                # if not holidays:
        holidays += self.env["hr.leave"].search(['&',('date_from', '>=', start_date),('date_to', '<=', end_date)])
                    
        total_day = 0

        for days in holidays:
            stat_name = days.holiday_status_id.name.lower()
            if "holiday" in stat_name:
                total_day += (days.date_to - days.date_from).days


        end_date = end_date + timedelta(days=total_day)
        
        return {
            'start_date' : self.timezonetoUTC8(start_date),
            'end_date' : self.timezonetoUTC8(end_date)
        }

    def timezonetoUTC8(self, date_from):
        return date_from + timedelta(hours=8)    